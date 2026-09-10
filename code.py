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

# الملفات الأساسية للحفظ النهائي
SAFE_FILE = "safe.json"
BANNED_FILE = "banned.json"

# جلسة العمل الحالية لقراءة ملف
current_session = {
    "filename": None,
    "words": [],
    "total_count": 0,
    "current_index": 0,
}


def append_to_json(filename: str, word: str):
    """دالة إضافة الكلمة إلى ملف JSON دون تكرار"""
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


def get_json_files():
    """البحث عن كل ملفات JSON المتاحة في مجلد السكربت"""
    files = [f for f in os.listdir(".") if f.endswith(".json")]
    return sorted(files)


def get_current_word_payload():
    """تجهيز النص والأزرار للكلمة الحالية داخل الملف المفتوح"""
    words = current_session["words"]
    idx = current_session["current_index"]
    total = current_session["total_count"]
    filename = current_session["filename"]

    # عند انتهاء جميع كلمات الملف
    if idx >= total or not words:
        return f"🎉 **أكتمل تصنيف جميع كلمات الملف:** `{filename}`", None

    word = words[idx]
    remaining = total - idx

    # معلومات الملف والنص الرئيسي
    text = (
        f"📁 **الملف الحالي:** `{filename}`\n"
        f"📊 **المعلومات:** الإجمالي: `{total}` | المتبقي: `{remaining}`\n"
        f"----------------------------------------\n"
        f"💬 **الكلمة المقترحة:** `{word}`\n\n"
        f"اختر التصنيف المناسب:"
    )

    buttons = [
        [
            Button.inline("✅ كلمة عادية", data=f"classify_safe:{word}"),
            Button.inline("❌ كلمة بذيئة", data=f"classify_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="classify_ignore")],
        [Button.inline("🔙 العودة للملفات", data="list_files")],
    ]

    return text, buttons


@client.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text_input = event.raw_text.strip() if event.raw_text else ""

    # --- أمر عرض واستعراض الملفات ---
    if text_input == "الملفات":
        json_files = get_json_files()
        if not json_files:
            return await event.reply("⚠️ لا توجد ملفات JSON في مجلد السكربت.")

        buttons = []
        for f in json_files:
            buttons.append([Button.inline(f"📄 {f}", data=f"open_file:{f}")])

        return await event.reply(
            "📁 **اختر الملف الذي تريد البدء بتصنيف كلماته:**", buttons=buttons
        )


# --- معالج الأزرار والتفاعل ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global current_session
    data = event.data.decode("utf-8")

    # 1. استعراض قائمة الملفات
    if data == "list_files":
        json_files = get_json_files()
        if not json_files:
            return await event.edit("⚠️ لا توجد ملفات JSON متاحة.")

        buttons = [[Button.inline(f"📄 {f}", data=f"open_file:{f}")] for f in json_files]
        return await event.edit("📁 **اختر ملفاً للاستعراض والتصنيف:**", buttons=buttons)

    # 2. فتح ملف محدد وعرض معلوماته
    elif data.startswith("open_file:"):
        filename = data.split("open_file:")[1]
        try:
            with open(filename, "r", encoding="utf-8") as f:
                loaded_words = json.load(f)

            if not isinstance(loaded_words, list) or not loaded_words:
                return await event.answer("⚠️ الملف فارغ أو بنيته غير صالحة!", alert=True)

            current_session["filename"] = filename
            current_session["words"] = loaded_words
            current_session["total_count"] = len(loaded_words)
            current_session["current_index"] = 0

            await event.answer(f"تم فتح {filename}")
            msg_text, buttons = get_current_word_payload()
            return await event.edit(msg_text, buttons=buttons)

        except Exception as e:
            return await event.answer(f"❌ خطأ في قراءة الملف: {e}", alert=True)

    # 3. تصنيف: كلمة عادية
    elif data.startswith("classify_safe:"):
        word = data.split("classify_safe:")[1]
        append_to_json(SAFE_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"✅ تم حفظ '{word}' في safe.json")

    # 4. تصنيف: كلمة بذيئة
    elif data.startswith("classify_ban:"):
        word = data.split("classify_ban:")[1]
        append_to_json(BANNED_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"❌ تم حفظ '{word}' في banned.json")

    # 5. تجاهل الكلمة
    elif data == "classify_ignore":
        current_session["current_index"] += 1
        await event.answer("🚫 تم التجاهل")

    # عرض الكلمة التالية تلقائياً مع تحديث العداد
    msg_text, buttons = get_current_word_payload()
    if buttons:
        await event.edit(msg_text, buttons=buttons)
    else:
        await event.edit(msg_text)




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
