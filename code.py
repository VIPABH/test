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

# الملفات الأساسية للحفظ
SAFE_FILE = "safe.json"
BANNED_FILE = "banned.json"

# إعدادات جلسة التجميع
sentences = set()
TARGET_WORD_COUNT = 50  # العدد الافتراضي للكلمات قبل حفظ الملف واستعراضه

# جلسة العمل الحالية للتصنيف
current_session = {
    "words": [],
    "total_count": 0,
    "current_index": 0,
}


def append_list_to_json(filename: str, new_words: list):
    """حفظ قائمة من الكلمات دفعة واحدة بدون تكرار"""
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    for word in new_words:
        if word not in data:
            data.append(word)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_to_json(filename: str, word: str):
    """إضافة كلمة واحدة إلى ملف JSON دون تكرار"""
    append_list_to_json(filename, [word])


def get_current_word_payload():
    """تجهيز النص والأزرار للكلمة الحالية داخل الجلسة"""
    words = current_session["words"]
    idx = current_session["current_index"]
    total = current_session["total_count"]

    if idx >= total or not words:
        return "🎉 **أكتمل تصنيف جميع الكلمات المحددة!**", None

    word = words[idx]
    remaining = total - idx

    text = (
        f"📊 **المعلومات:** الإجمالي: `{total}` | المتبقي: `{remaining}`\n"
        f"----------------------------------------\n"
        f"💬 **الكلمة المعروضة:** `{word}`\n\n"
        f"اختر الإجراء المناسب:"
    )

    buttons = [
        [
            Button.inline("✅ قبول (عادية)", data=f"classify_safe:{word}"),
            Button.inline("❌ رفض (بذيئة)", data=f"classify_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="classify_ignore")],
    ]

    return text, buttons


# --- معالج الرسائل وتجميع الكلمات ---
@client.on(events.NewMessage)
async def handler(event):
    global sentences, TARGET_WORD_COUNT, current_session

    sender = await event.get_sender()
    sender_id = event.sender_id

    # 1. أوامر المشرف wfffp (حصراً في الخاص)
    if event.is_private and sender_id == wfffp:
        text_input = event.raw_text.strip() if event.raw_text else ""

        # أمر تعديل عدد الكلمات المراد جمعها (مثال: الحد 100)
        if text_input.startswith("الحد"):
            parts = text_input.split()
            if len(parts) > 1 and parts[1].isdigit():
                TARGET_WORD_COUNT = int(parts[1])
                return await event.reply(
                    f"⚙️ تم تغيير عدد الكلمات المطلوبة للتجميع إلى: `{TARGET_WORD_COUNT}` كلمة."
                )

        # استعلام عن عدد الكلمات المجمعة حالياً
        elif text_input == "عدد الكلمات":
            return await event.reply(
                f"📊 عدد الكلمات المجمعة حالياً: `{len(sentences)}` / `{TARGET_WORD_COUNT}`"
            )

        # عرض الكلمات المجمعة حالياً يدوياً مع خيارات الفرز
        elif text_input == "استعراض":
            if not sentences:
                return await event.reply("⚠️ القائمة فارغة حالياً.")

            current_session["words"] = list(sentences)
            current_session["total_count"] = len(sentences)
            current_session["current_index"] = 0

            words_str = ", ".join(
                [f"`{w}`" for w in current_session["words"][:50]]
            )
            msg_text = (
                f"📋 **قائمة الكلمات المجمعة ({len(sentences)} كلمة):**\n\n"
                f"{words_str}\n\n"
                f"اختر طريقة المعالجة:"
            )

            buttons = [
                [Button.inline("✅ موافقة على الكل", data="approve_all")],
                [Button.inline("❌ مرفوضات (تعديل فردي)", data="start_individual")],
            ]
            return await event.reply(msg_text, buttons=buttons)

        # عند إرسال كلمة منفردة يدوياً من المشرف للفرز المباشر
        elif len(text_input.split()) == 1 and not text_input.startswith("/"):
            word = text_input
            text = f"💬 **الكلمة المرسلة:** `{word}`\n\nاختر الإجراء المناسب:"
            buttons = [
                [
                    Button.inline("✅ قبول (عادية)", data=f"classify_safe:{word}"),
                    Button.inline("❌ رفض (بذيئة)", data=f"classify_ban:{word}"),
                ],
                [Button.inline("🚫 تجاهل", data="classify_ignore")],
            ]
            return await event.reply(text, buttons=buttons)

    # 2. تجاهل البوتات والرسائل الفارغة أثناء التجميع العام
    if not sender or getattr(sender, "bot", False):
        return

    raw_text = event.raw_text.strip() if event.raw_text else ""
    if not raw_text:
        return

    # 3. استخراج وتجميع الكلمات المنفردة من جميع المحادثات
    words = re.findall(r"\b\w+\b", raw_text)

    for w in words:
        word = w.strip()
        if len(word) > 2 and not word.isdigit():
            sentences.add(word)

    # 4. عند الوصول إلى العدد المحدد (مثلاً 50 كلمة)
    if len(sentences) >= TARGET_WORD_COUNT:
        collected_words = list(sentences)[:TARGET_WORD_COUNT]

        # حفظ نسخة ملف JSON للاحتياط
        filename = f"words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(collected_words, f, ensure_ascii=False, indent=2)

        # إعداد جلسة العمل
        current_session["words"] = collected_words
        current_session["total_count"] = len(collected_words)
        current_session["current_index"] = 0

        # إرسال التنبيه والخيارات حصراً للمشرف wfffp في الخاص
        words_preview = ", ".join([f"`{w}`" for w in collected_words])
        caption_text = (
            f"✅ **تم جمع {len(collected_words)} كلمة بنجاح!**\n\n"
            f"📝 **الكلمات:**\n{words_preview}\n\n"
            f"اختر ما تريد القيام به:"
        )

        buttons = [
            [Button.inline("✅ موافقة على الكل", data="approve_all")],
            [Button.inline("❌ مرفوضات (تعديل فردي)", data="start_individual")],
        ]

        try:
            await client.send_file(
                wfffp, filename, caption=caption_text, buttons=buttons
            )
        except Exception as e:
            print(f"Error sending file to wfffp: {e}")

        sentences.clear()


# --- معالج الأزرار التفاعلية ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global current_session
    data = event.data.decode("utf-8")

    # الموافقة على جميع الكلمات دفعة واحدة وتخزينها في safe.json
    if data == "approve_all":
        words_to_save = current_session["words"]
        if words_to_save:
            append_list_to_json(SAFE_FILE, words_to_save)
            await event.answer("✅ تم قبول جميع الكلمات وحفظها في safe.json")
            return await event.edit(
                f"✅ **تم قبول وحفظ {len(words_to_save)} كلمة بنجاح في الكلمات العادية!**"
            )
        return await event.answer("⚠️ لا توجد كلمات للحفظ.")

    # بدء التصنيف والتعديل الفردي كلمة بكلمة
    elif data == "start_individual":
        current_session["current_index"] = 0
        msg_text, buttons = get_current_word_payload()
        return await event.edit(msg_text, buttons=buttons)

    # قبول كلمة واحدة
    elif data.startswith("classify_safe:"):
        word = data.split("classify_safe:")[1]
        append_to_json(SAFE_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"✅ تم القبول: {word}")

    # رفض كلمة واحدة (إضافتها للبذيئة)
    elif data.startswith("classify_ban:"):
        word = data.split("classify_ban:")[1]
        append_to_json(BANNED_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"❌ تم الرفض: {word}")

    # تجاهل الكلمة
    elif data == "classify_ignore":
        current_session["current_index"] += 1
        await event.answer("🚫 تم التجاهل")

    # عرض الكلمة التالية تلقائياً إذا كانت العملية فردية
    if current_session["words"]:
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
