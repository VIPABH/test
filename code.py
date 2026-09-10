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

# الخزان العام المستمر لاستقبال الكلمات (In-Memory Buffer)
sentences = set()

# ذاكرة المؤقت الشفافة (Staging Area) لتجنب I/O Bottleneck
staging_safe = set()
staging_banned = set()

FILTER_BATCH_SIZE = 50  # العدد المحدد لسحبه في كل دفعة فلترة

current_session = {
    "active_words": [],
    "total_count": 0,
    "current_index": 0,
    "awaiting_count": False,
}


def commit_staging_to_files():
    """كتابة الكلمات المجمعة في الذاكرة المؤقتة إلى الملفات دفعة واحدة وقفل العملية"""
    global staging_safe, staging_banned, sentences

    saved_safe_count = 0
    saved_banned_count = 0

    # 1. حفظ المقبول في safe.json
    if staging_safe:
        data = []
        if os.path.exists(SAFE_FILE):
            try:
                with open(SAFE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        for w in staging_safe:
            if w not in data:
                data.append(w)

        with open(SAFE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        saved_safe_count = len(staging_safe)

        # مسح الكلمات المحفوظة من خزان الاستماع الرئيسي
        sentences.difference_update(staging_safe)
        staging_safe.clear()

    # 2. حفظ المرفوض في banned.json
    if staging_banned:
        data = []
        if os.path.exists(BANNED_FILE):
            try:
                with open(BANNED_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        for w in staging_banned:
            if w not in data:
                data.append(w)

        with open(BANNED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        saved_banned_count = len(staging_banned)

        # مسح الكلمات المحفوظة من خزان الاستماع الرئيسي
        sentences.difference_update(staging_banned)
        staging_banned.clear()

    return saved_safe_count, saved_banned_count


def get_single_word_payload():
    """عرض الكلمة الحالية من الدفعة"""
    words = current_session["active_words"]
    idx = current_session["current_index"]
    total = current_session["total_count"]

    if idx >= total or not words:
        rem_in_buffer = len(sentences)
        text = (
            f"🎉 **اكتملت فلترة هذه الدفعة المؤقتة!**\n\n"
            f"📥 **الكلمات المقبولة بالذاكرة:** `{len(staging_safe)}` كلمة\n"
            f"🛑 **الكلمات المرفوضة بالذاكرة:** `{len(staging_banned)}` كلمة\n"
            f"📦 **المتبقي بالخزان العام:** `{rem_in_buffer}` كلمة\n\n"
            f"⚠️ **ملاحظة:** أرسل أمر **`تم`** لتطبيق الحفظ الدائم على الملفات."
        )
        buttons = [
            [
                Button.inline(
                    f"🔄 سحب {FILTER_BATCH_SIZE} كلمة جديدة",
                    data="pull_next_batch",
                )
            ]
        ]
        return text, buttons

    word = words[idx]
    remaining = total - idx

    text = (
        f"📊 **تصفية مؤقتة:** `{idx + 1}` من `{total}` (المتبقي بالدفعة: `{remaining}`)\n"
        f"📥 **بالذاكرة للموافقة:** `{len(staging_safe)}` | 🛑 **للرفض:** `{len(staging_banned)}`\n"
        f"----------------------------------------\n"
        f"💬 **الكلمة الحالية:** `{word}`\n\n"
        f"اختر الإجراء المناسب:"
    )

    buttons = [
        [
            Button.inline("✅ قبول مؤقت", data=f"single_safe:{word}"),
            Button.inline("❌ رفض مؤقت", data=f"single_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="single_ignore")],
    ]

    return text, buttons


# --- معالج الرسائل والأوامر النصية ---
@client.on(events.NewMessage)
async def handler(event):
    global sentences, FILTER_BATCH_SIZE, current_session

    sender = await event.get_sender()
    sender_id = event.sender_id

    # 1. أوامر المشرف wfffp بالخاص
    if event.is_private and sender_id == wfffp:
        text_input = event.raw_text.strip() if event.raw_text else ""

        # أمر تثبيت التغييرات والحفظ النهائـي للملفات (Commit)
        if text_input == "تم":
            if not staging_safe and not staging_banned:
                return await event.reply(
                    "⚠️ لا توجد تغييرات مؤقتة بالذاكرة لحفظها."
                )

            s_count, b_count = commit_staging_to_files()
            return await event.reply(
                f"💾 **تم كتابة التغييرات وإصدار التعديلات بنجاح!**\n\n"
                f"✅ **مقبولة أضيفت لـ safe.json:** `{s_count}` كلمة.\n"
                f"❌ **مرفوضة أضيفت لـ banned.json:** `{b_count}` كلمة.\n"
                f"📦 **المتبقي بالخزان العام:** `{len(sentences)}` كلمة."
            )

        # تحديد حجم السحب
        elif current_session.get("awaiting_count"):
            if text_input.isdigit():
                FILTER_BATCH_SIZE = int(text_input)
                current_session["awaiting_count"] = False
                return await event.reply(
                    f"⚙️ تم تحديد حجم دفعة الفلترة بـ: `{FILTER_BATCH_SIZE}` كلمة."
                )
            else:
                return await event.reply("⚠️ يرجى كتابة رقم صحيح فقط.")

        elif text_input.startswith("الحد"):
            parts = text_input.split()
            if len(parts) > 1 and parts[1].isdigit():
                FILTER_BATCH_SIZE = int(parts[1])
                return await event.reply(
                    f"⚙️ تم تغيير حجم الدفعة إلى: `{FILTER_BATCH_SIZE}` كلمة."
                )

        # طلب فلترة وتصفية دفعة
        elif text_input in ["فلترة", "استعراض"]:
            # فلترة الكلمات التي لم تُصنف بعد في staging
            unclassified = [
                w
                for w in sentences
                if w not in staging_safe and w not in staging_banned
            ]
            if not unclassified:
                return await event.reply(
                    "⚠️ لا توجد كلمات جديدة غير مصنفة بالخزان."
                )

            pulled_words = unclassified[:FILTER_BATCH_SIZE]
            current_session["active_words"] = pulled_words
            current_session["total_count"] = len(pulled_words)
            current_session["current_index"] = 0

            text, buttons = get_single_word_payload()
            return await event.reply(text, buttons=buttons)

        # الاستعلام عن الحالة الراهنة للذاكرة
        elif text_input in ["الحالة", "الذاكرة"]:
            return await event.reply(
                f"📊 **حالة النظام والذاكرة الحالية:**\n\n"
                f"📥 **مقبول مؤقت بالذاكرة:** `{len(staging_safe)}` كلمة\n"
                f"🛑 **مرفوض مؤقت بالذاكرة:** `{len(staging_banned)}` كلمة\n"
                f"📦 **إجمالي الخزان التراكمي:** `{len(sentences)}` كلمة\n\n"
                f"💡 أرسل **`تم`** لتفريغ الذاكرة وحفظ الملفات."
            )

    # 2. تجميع الكلمات المستمر بدون انقطاع
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


# --- معالج الأزرار والتفاعل الفوري بالذاكرة ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global current_session, FILTER_BATCH_SIZE
    data = event.data.decode("utf-8")

    # سحب الدفعة التالية
    if data == "pull_next_batch":
        unclassified = [
            w
            for w in sentences
            if w not in staging_safe and w not in staging_banned
        ]
        if not unclassified:
            return await event.answer(
                "⚠️ لا توجد كلمات جديدة بالخزان غير مصنفة!", alert=True
            )

        pulled_words = unclassified[:FILTER_BATCH_SIZE]
        current_session["active_words"] = pulled_words
        current_session["total_count"] = len(pulled_words)
        current_session["current_index"] = 0

        text, buttons = get_single_word_payload()
        return await event.edit(text, buttons=buttons)

    # قبول مؤقت (سريع جداً بالذاكرة فقط)
    elif data.startswith("single_safe:"):
        word = data.split("single_safe:")[1]
        staging_safe.add(word)
        staging_banned.discard(word)
        current_session["current_index"] += 1
        await event.answer("✅ قبول مؤقت")

    # رفض مؤقت (سريع جداً بالذاكرة فقط)
    elif data.startswith("single_ban:"):
        word = data.split("single_ban:")[1]
        staging_banned.add(word)
        staging_safe.discard(word)
        current_session["current_index"] += 1
        await event.answer("❌ رفض مؤقت")

    # تجاهل الكلمة
    elif data == "single_ignore":
        current_session["current_index"] += 1
        await event.answer("🚫 تجاهل")

    # تحديث واجهة العرض للكلمة التالية
    if current_session.get("active_words"):
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
