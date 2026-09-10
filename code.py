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

# إعدادات حالة التجميع والجلسة
sentences = set()
TARGET_WORD_COUNT = 50  # العدد الافتراضي للكلمات في الدفعة

current_session = {
    "words": [],
    "total_count": 0,
    "current_index": 0,
    "awaiting_count_input": False,  # ينتظر إدخال عدد جديد من المستخدم
}


def append_list_to_json(filename: str, new_words: list):
    """حفظ قائمة كلمات دفعة واحدة في ملف JSON دون تكرار"""
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
    """حفظ كلمة واحدة في ملف JSON دون تكرار"""
    append_list_to_json(filename, [word])


def get_single_word_payload():
    """تجهيز الكلمة الفردية الحالية مع أزرار الفرز"""
    words = current_session["words"]
    idx = current_session["current_index"]
    total = current_session["total_count"]

    if idx >= total or not words:
        return (
            "🎉 **اكتمل فرز وتعديل جميع الكلمات في هذه الدفعة!**",
            [[Button.inline("🔙 القائمة الرئيسية", data="main_menu")]],
        )

    word = words[idx]
    remaining = total - idx

    text = (
        f"📊 **فرز فردي:** `{idx + 1}` من `{total}` (المتبقي: `{remaining}`)\n"
        f"----------------------------------------\n"
        f"💬 **الكلمة الحالية:** `{word}`\n\n"
        f"اختر الإجراء المطلوب:"
    )

    buttons = [
        [
            Button.inline("✅ قبول فردي (عادية)", data=f"single_safe:{word}"),
            Button.inline("❌ رفض فردي (بذيئة)", data=f"single_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="single_ignore")],
    ]

    return text, buttons


def get_batch_payload():
    """تجهيز العرض الجماعي للدفعة الكاملة مع الأزرار العامة"""
    words = current_session["words"]
    total = len(words)

    words_preview = "\n".join(
        [f"{i+1}. `{w}`" for i, w in enumerate(words[:50])]
    )
    if total > 50:
        words_preview += f"\n\n...و `{total - 50}` كلمة أخرى."

    text = (
        f"📦 **دفعة الكلمات المجمعة ({total} كلمة):**\n\n"
        f"{words_preview}\n\n"
        f"اختر كيفية التعامل مع هذه الدفعة:"
    )

    buttons = [
        [Button.inline("✅ موافقة على الكل", data="batch_approve_all")],
        [
            Button.inline(
                "❌ فرز وتعديل فردي (كلمة بكلمة)", data="start_single_mode"
            )
        ],
        [
            Button.inline("⚙️ تحديد عدد الكلمات", data="change_count_prompt"),
            Button.inline("🗑 تجاهل الدفعة", data="batch_ignore"),
        ],
    ]

    return text, buttons


# --- معالج الرسائل والأوامر النصية ---
@client.on(events.NewMessage)
async def handler(event):
    global sentences, TARGET_WORD_COUNT, current_session

    sender = await event.get_sender()
    sender_id = event.sender_id

    # 1. تخصيص الأوامر والخاص للمشرف wfffp
    if event.is_private and sender_id == wfffp:
        text_input = event.raw_text.strip() if event.raw_text else ""

        # إذا كان البوت ينتظر من الأدمن إدخال رقم محدد للدفعة
        if current_session.get("awaiting_count_input"):
            if text_input.isdigit():
                TARGET_WORD_COUNT = int(text_input)
                current_session["awaiting_count_input"] = False
                return await event.reply(
                    f"✅ تم تعديل عدد كلمات الدفعة إلى: `{TARGET_WORD_COUNT}` كلمة."
                )
            else:
                return await event.reply(
                    "⚠️ يرجى إرسال رقم صحيح فقط لتحديد العدد."
                )

        # تغيير عدد الكلمات عبر الأمر المباشر (مثال: الحد 30)
        if text_input.startswith("الحد"):
            parts = text_input.split()
            if len(parts) > 1 and parts[1].isdigit():
                TARGET_WORD_COUNT = int(parts[1])
                return await event.reply(
                    f"⚙️ تم تغيير حجم الدفعة إلى: `{TARGET_WORD_COUNT}` كلمة."
                )

        # استعراض الكلمات المجمعة حالياً
        elif text_input in ["استعراض", "الكلمات"]:
            if not sentences:
                return await event.reply("⚠️ لا توجد كلمات مجمعة حالياً.")

            current_session["words"] = list(sentences)
            current_session["total_count"] = len(sentences)
            current_session["current_index"] = 0

            text, buttons = get_batch_payload()
            return await event.reply(text, buttons=buttons)

        # عند إرسال كلمة واحدة يدوياً بالخاص لتصنيفها فوراً
        elif len(text_input.split()) == 1 and not text_input.startswith("/"):
            current_session["words"] = [text_input]
            current_session["total_count"] = 1
            current_session["current_index"] = 0

            text, buttons = get_single_word_payload()
            return await event.reply(text, buttons=buttons)

    # 2. تجميع الكلمات من المجموعات والمحادثات (تجاهل البوتات)
    if not sender or getattr(sender, "bot", False):
        return

    raw_text = event.raw_text.strip() if event.raw_text else ""
    if not raw_text:
        return

    words = re.findall(r"\b\w+\b", raw_text)
    for w in words:
        word = w.strip()
        if len(word) > 2 and not word.isdigit():
            sentences.add(word)

    # 3. عند الوصول للعدد المحدد من الكلمات
    if len(sentences) >= TARGET_WORD_COUNT:
        collected_words = list(sentences)[:TARGET_WORD_COUNT]

        # إعداد بيانات الجلسة للدفعة
        current_session["words"] = collected_words
        current_session["total_count"] = len(collected_words)
        current_session["current_index"] = 0

        sentences.clear()

        text, buttons = get_batch_payload()
        try:
            await client.send_message(wfffp, text, buttons=buttons)
        except Exception as e:
            print(f"فشل إرسال الدفعة للمشرف: {e}")


# --- معالج الأزرار والتفاعل ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global current_session, TARGET_WORD_COUNT
    data = event.data.decode("utf-8")

    # 1. الموافقة على الدفعة كاملة بحركة واحدة
    if data == "batch_approve_all":
        words_to_save = current_session.get("words", [])
        if words_to_save:
            append_list_to_json(SAFE_FILE, words_to_save)
            await event.answer("✅ تم قبول جميع الكلمات وحفظها!")
            return await event.edit(
                f"✅ **تم قبول وحفظ {len(words_to_save)} كلمة بنجاح في `{SAFE_FILE}`!**"
            )
        return await event.answer("⚠️ لا توجد كلمات للحفظ.")

    # 2. بدء نمط الفرز الفردي (كلمة كلمة)
    elif data == "start_single_mode":
        current_session["current_index"] = 0
        text, buttons = get_single_word_payload()
        return await event.edit(text, buttons=buttons)

    # 3. طلّب تحديد عدد الكلمات
    elif data == "change_count_prompt":
        current_session["awaiting_count_input"] = True
        await event.answer("أرسل الرقم المطلوب في المحادثة الآن")
        return await event.edit(
            f"⚙️ **العدد الحالي للدفعة:** `{TARGET_WORD_COUNT}`\n\n"
            f"يرجى كتابة وإرسال العدد الجديد للكلمات مباشرة في الشات:"
        )

    # 4. تجاهل الدفعة كاملة
    elif data == "batch_ignore":
        current_session["words"] = []
        await event.answer("🗑 تم تجاهل الدفعة")
        return await event.edit("🗑 **تمت إزالة الدفعة وتجاهلها.**")

    # 5. قبول فردي للكلمة الحالية والتأهل للكلمة التالية
    elif data.startswith("single_safe:"):
        word = data.split("single_safe:")[1]
        append_to_json(SAFE_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"✅ تم القبول: {word}")

    # 6. رفض فردي للكلمة الحالية (إضافتها للبذيئة) والتأهل للكلمة التالية
    elif data.startswith("single_ban:"):
        word = data.split("single_ban:")[1]
        append_to_json(BANNED_FILE, word)
        current_session["current_index"] += 1
        await event.answer(f"❌ تم الرفض: {word}")

    # 7. تجاهل الكلمة الحالية والتأهل للكلمة التالية
    elif data == "single_ignore":
        current_session["current_index"] += 1
        await event.answer("🚫 تم التجاهل")

    # 8. القائمة الرئيسية
    elif data == "main_menu":
        text, buttons = get_batch_payload()
        return await event.edit(text, buttons=buttons)

    # عند الاستمرار في الفرز الفردي: يتم الاستماع وإظهار الكلمة التالية تلقائياً
    if current_session.get("words"):
        text, buttons = get_single_word_payload()
        await event.edit(text, buttons=buttons)


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
