import asyncio
from datetime import datetime
import json
import os
import random
import re
import warnings

warnings.filterwarnings("ignore")

import joblib
from ABH import ABH as client
from Resources import *
from telethon import Button, events

# 1. تحميل الموديل الذكي
print("⏳ جاري تحميل الموديل...")
MODEL_PATH = "model.joblib"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ تم تحميل الموديل بنجاح!")
else:
    model = None
    print("⚠️ لم يتم العثور على ملف model.joblib!")


def normalize_arabic_text(text: str) -> str:
    """توحيد النصوص العربية لضمان تطابق الفحص مع تدريب الموديل"""
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة\b", "ه", text)
    text = re.sub(r"ى\b", "ي", text)
    text = re.sub(r"[\u064B-\u0652\u0640]", "", text)  # إزالة التشكيل والتطويل
    return text.strip()


def check_profanity_ai_only(text: str) -> tuple[bool, float, str]:
    """دالة الفحص المعتمدة على الذكاء الاصطناعي حصراً (كلمة بكلمة)"""
    if not text or not text.strip() or model is None:
        return False, 0.0, "نص فارغ أو الموديل غير محمل"

    clean_text = normalize_arabic_text(text)
    words = clean_text.split()

    max_prob = 0.0
    flagged_word = ""

    # فحص كل كلمة بشكل منفصل عبر الذكاء الاصطناعي
    for word in words:
        # تجنب الكلمات القصيرة جداً (حرفين أو أقل) لتفادي البلاغات الخاطئة
        if len(word) <= 2:
            continue

        try:
            # حساب احتمال أن تكون الكلمة بذيئة
            prob = model.predict_proba([word])[0][1]

            if prob > max_prob:
                max_prob = prob
                flagged_word = word
        except Exception as e:
            continue

    # العتبة 95%: يتم تعليم الرسالة فقط إذا كان الموديل متأكداً بنسبة 95% أو أعلى
    if max_prob >= 0.95:
        return True, max_prob, f"تكهن الموديل الذكي على الكلمة: '{flagged_word}'"

    return False, max_prob, "نص سليم"


@client.on(events.NewMessage)
async def monitor_messages(event):
    # تجاهل رسائل البوتات والقنوات والرسائل الفارغة
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text = event.raw_text
    if not text:
        return

    # فحص الرسالة عبر الذكاء الاصطناعي فقط
    is_flagged, confidence, reason = check_profanity_ai_only(text)

    if is_flagged:
        try:
            # 1. استخراج رابط الرسالة
            chat = await event.get_chat()
            if getattr(chat, "username", None):
                msg_link = f"https://t.me/{chat.username}/{event.id}"
            else:
                clean_chat_id = str(event.chat_id).replace("-100", "")
                msg_link = f"https://t.me/c/{clean_chat_id}/{event.id}"

            # 2. معلومات المرسل
            first_name = sender.first_name or "بدون اسم"
            last_name = f" {sender.last_name}" if sender.last_name else ""
            full_name = f"{first_name}{last_name}"
            username = f"@{sender.username}" if sender.username else "لا يوجد"
            user_id = sender.id

            # 3. إعداد التقرير الإشعاري
            report_text = (
                f"🚨 **رصد كلام بذيء ({confidence * 100:.1f}%)**\n\n"
                f"👤 **معلومات المرسل:**\n"
                f"• **الاسم:** [{full_name}](tg://user?id={user_id})\n"
                f"• **اليوزر:** {username}\n"
                f"• **الآيدي:** `{user_id}`\n\n"
                f"📝 **النص:**\n`{text}`\n\n"
                f"🔍 **السبب:** `{reason}`\n"
                f"📊 **نسبة التوقع:** `{confidence * 100:.1f}%`\n\n"
                f"🔗 **رابط الرسالة:** [الانتقال للرسالة]({msg_link})"
            )

            # 4. إرسال التقرير
            await client.send_message(wfffp, report_text, link_preview=False)

        except Exception as e:
            print(f"خطأ أثناء إرسال التقرير: {e}")
