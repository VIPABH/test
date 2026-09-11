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


def check_profanity_high_confidence(text: str) -> tuple[bool, float, str]:
    """دالة الفحص باستخدام الموديل مباشرة على النص الخام بدون أي تنظيف أو توحيد"""
    if not text or not text.strip():
        return False, 0.0, "نص فارغ"

    if model is not None:
        try:
            # التنبؤ المباشر على النص الأصلي كما هو
            prob = model.predict_proba([text])[0][1]

            # العتبة 95%
            if prob >= 0.95:
                return True, prob, "تكهن الموديل الذكي (ثقة عالية)"
            return False, prob, "نص سليم"

        except Exception as e:
            print(f"خطأ أثناء التنبؤ: {e}")
            return False, 0.0, "خطأ في الموديل"

    return False, 0.0, "الموديل غير محمل"


@client.on(events.NewMessage)
async def monitor_messages(event):
    # تجاهل رسائل البوتات والقنوات والرسائل الفارغة
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text = event.raw_text
    if not text:
        return

    # فحص الرسالة بالنص الخام
    is_flagged, confidence, reason = check_profanity_high_confidence(text)

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
                f"🚨 **رصد كلام بذيء عبر الذكاء الاصطناعي ({confidence * 100:.1f}%)**\n\n"
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
