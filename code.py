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

# 1. قائمة الكلمات المحظورة المباشرة (مطابقة صريحة 100%)
RAW_BANNED_WORDS = [
    "كس",
    "كسمك",
    "كسختك",
    "عير",
    "كسخالتك",
    "خرا",
    "كحاب",
    "مناويج",
    "كحبه",
    "ابن الكحبه",
    "فرخ",
    "فروخ",
    "طيزك",
    "طيزختك",
    "شرموط",
    "شرموطه",
    "ابن الشرموطه",
    "ابن الخول",
    "ابن العرص",
    "منايك",
    "متناك",
    "ابن المتناكه",
    "زبك",
    "عرص",
    "زبي",
    "خول",
    "لبوه",
    "منيوك",
    "قحبه",
    "القحبه",
    "شراميط",
    "العلق",
    "تيز",
    "التيز",
    "الديوث",
    "كسمج",
    "بلبولك",
    "صدرج",
    "كسعرضك",
    "الخنيث",
    "نغل",
    "نغولة",
    "انيجة",
    "انيج",
    "عاهرات",
    "عاهرة",
    "طيز",
    "كواد",
    "بربوك",
    "زب",
    "الكواد",
    "دودة",
    "كسك",
    "سكسي",
    "ابن الزنا",
    "قحبة",
    "عيري",
    "نودز",
    "قضيب",
]

BANNED_SET = set(RAW_BANNED_WORDS)

# 2. تحميل الموديل الذكي باسمه الصحيح
print("⏳ جاري تحميل الموديل...")
MODEL_PATH = "model.joblib"  # المطابق لملف Colab
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ تم تحميل الموديل بنجاح!")
else:
    model = None
    print("⚠️ لم يتم العثور على ملف model.joblib!")


def normalize_arabic_text(text: str) -> str:
    """توحيد الألفات والتاء والياء لضمان تطابق الفحص مع تدريب الموديل"""
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة\b", "ه", text)
    text = re.sub(r"ى\b", "ي", text)
    text = re.sub(r"[\u064B-\u0652\u0640]", "", text)  # إزالة التشكيل والتطويل
    return text.strip()


def check_profanity_high_confidence(text: str) -> tuple[bool, float, str]:
    """دالة الفحص باستخدام التطابق الصريح أولاً ثم التنبؤ بالذكاء الاصطناعي"""
    if not text or not text.strip():
        return False, 0.0, "نص فارغ"

    clean_text = normalize_arabic_text(text)
    words = clean_text.split()

    # 1. مطابقة صريحة مباشرة من القائمة (100%)
    for word in words:
        if word in BANNED_SET or normalize_arabic_text(word) in BANNED_SET:
            return True, 1.0, f"مطابقة صريحة (100%): '{word}'"

    # 2. التنبؤ عبر الموديل الذكي (إذا كان محمولاً)
    if model is not None:
        try:
            # التنبؤ على النص المنظف
            prob = model.predict_proba([clean_text])[0][1]

            # العتبة 85% للحد من البلاغات الخاطئة
            if prob >= 0.95:
                return True, prob, "تكهن الموديل الذكي (ثقة عالية)"
            return False, prob, "نص سليم"
        except Exception as e:
            print(f"خطأ أثناء التنبؤ: {e}")
            return False, 0.0, "خطأ في الموديل"

    return False, 0.0, "نص سليم"


@client.on(events.NewMessage)
async def monitor_messages(event):
    # تجاهل رسائل البوتات والقنوات والرسائل الفارغة
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text = event.raw_text
    if not text:
        return

    # فحص الرسالة
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

            # 4. إرسال التقرير (تأكد من معرف wfffp أنه ايدي روم الإشعارات أو الإدمن)
            await client.send_message(wfffp, report_text, link_preview=False)

        except Exception as e:
            print(f"خطأ أثناء إرسال التقرير: {e}")
