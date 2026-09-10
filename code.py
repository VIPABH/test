import asyncio
from datetime import datetime
import json
import os
import random
import re
import warnings

warnings.filterwarnings("ignore")

from ABH import ABH as client
import joblib
from Resources import *
from telethon import Button, events

# اسم الملفات المحلية للحفظ
SAFE_FILE = "safe.json"
BANNED_FILE = "banned.json"

sentences = set()  # تجميع الكلمات المنفردة


def append_to_json(filename: str, word: str):
    """دالة مساعدة لإضافة الكلمة إلى ملف JSON دون تكرار"""
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    if word not in data:
        data.append(word)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_word_message():
    """دالة مساعدة لاستخراج كلمة عشوائية مع الأزرار 3"""
    if not sentences:
        return "⚠️ القائمة فارغة حالياً.", None

    word = random.choice(list(sentences))

    buttons = [
        [
            Button.inline("✅ كلمة عادية", data=f"add_safe:{word}"),
            Button.inline("❌ كلمة بذيئة", data=f"add_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="ignore_word")],
    ]

    text = f"💬 **الكلمة المقترحة:** `{word}`\n\nاختر التصنيف المناسب:"
    return text, buttons


@client.on(events.NewMessage)
async def handler(event):
    global sentences

    # 1. تجاهل رسائل البوتات والرسائل الفارغة
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text_input = event.raw_text.strip() if event.raw_text else ""
    if not text_input:
        return

    # --- الأوامر المباشرة ---
    if text_input == "عدد الكلمات":
        return await event.reply(f"📊 عدد الكلمات المجمعة: `{len(sentences)}`")

    elif text_input == "كلمة عشوائية":
        msg_text, buttons = get_next_word_message()
        if buttons:
            return await event.reply(msg_text, buttons=buttons)
        return await event.reply(msg_text)

    # 2. تقسيم النص إلى كلمات منفردة وتجاهل الرموز وعلامات الترقيم
    words = re.findall(r"\b\w+\b", text_input)

    for w in words:
        word = w.strip()
        if len(word) > 2 and not word.isdigit():
            sentences.add(word)

    # 3. عند الوصول إلى 1000 كلمة
    if len(sentences) >= 1000:
        data_to_save = list(sentences)[:1000]

        filename = f"words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        await client.send_file(
            wfffp,
            filename,
            caption=f"✅ تم جمع وحفظ {len(data_to_save)} كلمة بنجاح!",
        )

        sentences.clear()


# --- معالج الضغط على الأزرار ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global sentences
    data = event.data.decode("utf-8")

    # 1. إضافة للكلمات العادية وحذفها من الـ Set
    if data.startswith("add_safe:"):
        word = data.split("add_safe:")[1]
        append_to_json(SAFE_FILE, word)
        sentences.discard(word)  # إزالة الكلمة حتى لا تتكرر
        await event.answer(f"✅ تم حفظ '{word}' في الكلمات العادية")

    # 2. إضافة للكلمات البذيئة وحذفها من الـ Set
    elif data.startswith("add_ban:"):
        word = data.split("add_ban:")[1]
        append_to_json(BANNED_FILE, word)
        sentences.discard(word)  # إزالة الكلمة حتى لا تتكرر
        await event.answer(f"❌ تم حفظ '{word}' في الكلمات البذيئة")

    # 3. تجاهل الكلمة الحالية
    elif data == "ignore_word":
        await event.answer("🚫 تم التجاهل")

    # عرض الكلمة التالية فوراً لتسريع عملية الفرز
    msg_text, buttons = get_next_word_message()
    if buttons:
        await event.edit(msg_text, buttons=buttons)
    else:
        await event.edit("⚠️ اكتمل تصنيف الكلمات أو أن القائمة فارغة حالياً!")



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

# تحميل الموديل الذكي
print("جاري تحميل الموديل...")
model = joblib.load("profanity_model.joblib")
print("تم تحميل الموديل بنجاح!")


def check_profanity_high_confidence(text: str) -> tuple[bool, float, str]:
    """دالة الفحص بعد رفع العتبة إلى 85% للموديل الذكي لتفادي التنبيهات الكاذبة"""
    if not text:
        return False, 0.0, "نص فارغ"

    words = re.findall(r"\w+", text.lower())

    # 1. مطابقة صريحة مباشرة من القائمة (100%)
    for word in words:
        if word in BANNED_SET:
            return True, 1.0, f"مطابقة صريحة (100%): '{word}'"

    # 2. حساب نسبة التوقع من الموديل الذكي
    prob = model.predict_proba([text])[0][1]

    # العتبة المرفوعة: يجب أن تكون النسبة 85% (0.85) أو أعلى
    if prob >= 0.85:
        return True, prob, "تكهن الموديل الذكي (ثقة عالية)"

    return False, prob, "نص سليم"


@client.on(events.NewMessage)
async def monitor_messages(event):
    # تجاهل الرسائل الفارغة أو القادمة من البوتات
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

            # إرسال التقرير
            await client.send_message(wfffp, report_text, link_preview=False)

        except Exception as e:
            print(f"خطأ أثناء إرسال التقرير: {e}")
