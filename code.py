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

# الخزان العام المستمر لتجميع الكلمات بالذاكرة (In-Memory Buffer)
sentences = set()

# الذاكرة المؤقتة (Staging Area) لمنع I/O Bottleneck
staging_safe = set()
staging_banned = set()

CHUNK_SIZE = 50  # حجم الجنك (الدفعة) الافتراضي

current_session = {
    "chunk_words": [],  # كلمات الجنك الحالي
    "total_count": 0,
    "current_index": 0,
    "mode": "chunk",  # 'chunk' (عرض الجنك) أو 'single' (فرز فردي)
    "awaiting_chunk_size": False,
}


def commit_staging_to_files():
    """حفظ التغيرات المؤقتة إلى الملفات دفعة واحدة وقفل العملية"""
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
        sentences.difference_update(staging_banned)
        staging_banned.clear()

    return saved_safe_count, saved_banned_count


def get_chunk_payload():
    """واجهة عرض الجنك (الدفعة الكاملة)"""
    words = current_session["chunk_words"]
    total = len(words)
    unclassified_total = len(
        [
            w
            for w in sentences
            if w not in staging_safe and w not in staging_banned
        ]
    )

    words_preview = "\n".join(
        [f"{i+1}. `{w}`" for i, w in enumerate(words[:50])]
    )

    text = (
        f"📦 **جنك كلمات حالي ({total} كلمة):**\n"
        f"📊 **إجمالي الكلمات الغير مفلترة بالخزان:** `{unclassified_total}` كلمة\n"
        f"📥 **مقبول بالذاكرة:** `{len(staging_safe)}` | 🛑 **مرفوض:** `{len(staging_banned)}`\n"
        f"----------------------------------------\n"
        f"{words_preview}\n\n"
        f"اختر كيفية تصنيف هذا الجنك:"
    )

    buttons = [
        [
            Button.inline(
                "✅ قبول الجنك كاملاً (مؤقت)", data="chunk_approve_all"
            ),
            Button.inline("❌ رفض الجنك كاملاً (مؤقت)", data="chunk_ban_all"),
        ],
        [Button.inline("🔍 فرز فردي (كلمة كلمة)", data="start_single_mode")],
        [
            Button.inline("🔄 جنك جديد", data="pull_next_chunk"),
            Button.inline("⚙️ حجم الجنك", data="change_chunk_size_prompt"),
        ],
    ]

    return text, buttons


def get_single_word_payload():
    """واجهة العرض الفردي (كلمة بكلمة داخل الجنك)"""
    words = current_session["chunk_words"]
    idx = current_session["current_index"]
    total = current_session["total_count"]

    if idx >= total or not words:
        text = (
            f"🎉 **اكتمل فرز هذا الجنك فردياً!**\n\n"
            f"📥 **مقبول مؤقت بالذاكرة:** `{len(staging_safe)}` كلمة\n"
            f"🛑 **مرفوض مؤقت بالذاكرة:** `{len(staging_banned)}` كلمة\n\n"
            f"💡 أرسل **`تم`** لتثبيت التعديلات بالملفات أو اسحب جنك جديد."
        )
        buttons = [
            [
                Button.inline(
                    f"🔄 سحب الجنك التالي ({CHUNK_SIZE} كلمة)",
                    data="pull_next_chunk",
                )
            ],
            [Button.inline("📋 العودة لرجوع الجنك", data="show_chunk_view")],
        ]
        return text, buttons

    word = words[idx]
    remaining = total - idx

    text = (
        f"🔍 **فرز فردي:** `{idx + 1}` من `{total}` (المتبقي بالجنك: `{remaining}`)\n"
        f"📥 **بالذاكرة مقبول:** `{len(staging_safe)}` | 🛑 **مرفوض:** `{len(staging_banned)}`\n"
        f"----------------------------------------\n"
        f"💬 **الكلمة الحالية:** `{word}`\n\n"
        f"اختر الإجراء المناسب:"
    )

    buttons = [
        [
            Button.inline("✅ قبول فردي", data=f"single_safe:{word}"),
            Button.inline("❌ رفض فردي", data=f"single_ban:{word}"),
        ],
        [Button.inline("🚫 تجاهل", data="single_ignore")],
        [Button.inline("🔙 العودة للجنك", data="show_chunk_view")],
    ]

    return text, buttons


# --- معالج الرسائل واستقبال الأوامر ---
@client.on(events.NewMessage)
async def handler(event):
    global sentences, CHUNK_SIZE, current_session

    sender = await event.get_sender()
    sender_id = event.sender_id

    # 1. أوامر المشرف wfffp بالخاص
    if event.is_private and sender_id == wfffp:
        text_input = event.raw_text.strip() if event.raw_text else ""

        # أمر تثبيت التغييرات والحفظ النهائـي من الذاكرة إلى الملفات (Commit)
        if text_input == "تم":
            if not staging_safe and not staging_banned:
                return await event.reply(
                    "⚠️ لا توجد تعديلات مؤقتة بالذاكرة لحفظها."
                )

            s_count, b_count = commit_staging_to_files()
            return await event.reply(
                f"💾 **تم كتابة التغييرات بنجاح لتجنب Bottleneck!**\n\n"
                f"✅ **أضيفت لـ safe.json:** `{s_count}` كلمة.\n"
                f"❌ **أضيفت لـ banned.json:** `{b_count}` كلمة.\n"
                f"📦 **المتبقي بالخزان العام:** `{len(sentences)}` كلمة."
            )

        # تحديد حجم الجنك من الإدخال
        elif current_session.get("awaiting_chunk_size"):
            if text_input.isdigit():
                CHUNK_SIZE = int(text_input)
                current_session["awaiting_chunk_size"] = False
                return await event.reply(
                    f"⚙️ تم تحديد حجم الجنك بـ: `{CHUNK_SIZE}` كلمة."
                )
            else:
                return await event.reply("⚠️ يرجى كتابة رقم صحيح فقط.")

        elif text_input.startswith("الجنك") or text_input.startswith("الحد"):
            parts = text_input.split()
            if len(parts) > 1 and parts[1].isdigit():
                CHUNK_SIZE = int(parts[1])
                return await event.reply(
                    f"⚙️ تم تغيير حجم الجنك إلى: `{CHUNK_SIZE}` كلمة."
                )

        # طلب سحب جنك جديد للفلترة
        elif text_input in ["جنك", "فلترة", "استعراض"]:
            unclassified = [
                w
                for w in sentences
                if w not in staging_safe and w not in staging_banned
            ]
            if not unclassified:
                return await event.reply(
                    "⚠️ لا توجد كلمات جديدة غير مصنفة بالخزان."
                )

            pulled_words = unclassified[:CHUNK_SIZE]
            current_session["chunk_words"] = pulled_words
            current_session["total_count"] = len(pulled_words)
            current_session["current_index"] = 0
            current_session["mode"] = "chunk"

            text, buttons = get_chunk_payload()
            return await event.reply(text, buttons=buttons)

        # عرض حالة الذاكرة
        elif text_input in ["الحالة", "الذاكرة"]:
            return await event.reply(
                f"📊 **حالة الذاكرة الحالية:**\n\n"
                f"📥 **مقبول مؤقت:** `{len(staging_safe)}` كلمة\n"
                f"🛑 **مرفوض مؤقت:** `{len(staging_banned)}` كلمة\n"
                f"📦 **الخزان العام التراكمي:** `{len(sentences)}` كلمة\n\n"
                f"💡 أرسل **`تم`** لكتابة التغييرات إلى الملفات."
            )
        text = event.text
        buttons = [
        
            Button.inline("✅ قبول فردي", data=f"single_safe:{text}"),
            Button.inline("❌ رفض فردي", data=f"single_ban:{text}"),
        ]
        await event.reply(f"شنو تحب تسوي وي `{text}`", buttons=buttons)
    # 2. التجميع المستمر من كل المحادثات والمجموعات
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


# --- معالج الأزرار والتفاعل (جنكات وفردي) ---
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global current_session, CHUNK_SIZE
    data = event.data.decode("utf-8")

    # سحب الجنك التالي
    if data == "pull_next_chunk":
        unclassified = [
            w
            for w in sentences
            if w not in staging_safe and w not in staging_banned
        ]
        if not unclassified:
            return await event.answer(
                "⚠️ لا توجد كلمات جديدة غير مصنفة!", alert=True
            )

        pulled_words = unclassified[:CHUNK_SIZE]
        current_session["chunk_words"] = pulled_words
        current_session["total_count"] = len(pulled_words)
        current_session["current_index"] = 0
        current_session["mode"] = "chunk"

        text, buttons = get_chunk_payload()
        return await event.edit(text, buttons=buttons)

    # قبول الجنك كاملاً في الذاكرة
    elif data == "chunk_approve_all":
        words_in_chunk = current_session.get("chunk_words", [])
        for w in words_in_chunk:
            staging_safe.add(w)
            staging_banned.discard(w)

        await event.answer("✅ تم قبول جميع كلمات الجنك بالذاكرة")
        return await event.edit(
            f"✅ **تم قبول جنك كامل ({len(words_in_chunk)} كلمة) مؤقتاً بالذاكرة!**\n\n"
            f"💡 أرسل **`تم`** للحفظ النهائي أو اضغط أدناه لسحب جنك جديد:",
            buttons=[
                [
                    Button.inline(
                        f"🔄 سحب الجنك التالي ({CHUNK_SIZE})",
                        data="pull_next_chunk",
                    )
                ]
            ],
        )

    # رفض الجنك كاملاً في الذاكرة
    elif data == "chunk_ban_all":
        words_in_chunk = current_session.get("chunk_words", [])
        for w in words_in_chunk:
            staging_banned.add(w)
            staging_safe.discard(w)

        await event.answer("❌ تم رفض جميع كلمات الجنك بالذاكرة")
        return await event.edit(
            f"❌ **تم نقل جنك كامل ({len(words_in_chunk)} كلمة) للمرفوضات بالذاكرة!**\n\n"
            f"💡 أرسل **`تم`** للحفظ النهائي أو اضغط أدناه لسحب جنك جديد:",
            buttons=[
                [
                    Button.inline(
                        f"🔄 سحب الجنك التالي ({CHUNK_SIZE})",
                        data="pull_next_chunk",
                    )
                ]
            ],
        )

    # التحويل للفرز الفردي داخل الجنك الحالي
    elif data == "start_single_mode":
        current_session["mode"] = "single"
        current_session["current_index"] = 0
        text, buttons = get_single_word_payload()
        return await event.edit(text, buttons=buttons)

    # العودة للواجهة الجماعية للجنك
    elif data == "show_chunk_view":
        current_session["mode"] = "chunk"
        text, buttons = get_chunk_payload()
        return await event.edit(text, buttons=buttons)

    # طلب تغيير حجم الجنك
    elif data == "change_chunk_size_prompt":
        current_session["awaiting_chunk_size"] = True
        await event.answer("أرسل الرقم المطلوب للجنك")
        return await event.edit(
            f"⚙️ **حجم الجنك الحالي:** `{CHUNK_SIZE}` كلمة\n\n"
            f"أرسل الرقم الجديد للجنك مباشرة في المحادثة:"
        )

    # --- معالجة الفرز الفردي داخل الجنك ---
    elif data.startswith("single_safe:"):
        word = data.split("single_safe:")[1]
        staging_safe.add(word)
        staging_banned.discard(word)
        current_session["current_index"] += 1
        await event.answer("✅ قبول")

    elif data.startswith("single_ban:"):
        word = data.split("single_ban:")[1]
        staging_banned.add(word)
        staging_safe.discard(word)
        current_session["current_index"] += 1
        await event.answer("❌ رفض")

    elif data == "single_ignore":
        current_session["current_index"] += 1
        await event.answer("🚫 تجاهل")

    # تحديث تلقائي للواجهة بناءً على النمط المحدد (جنك / فردي)
    if current_session.get("chunk_words"):
        if current_session["mode"] == "single":
            text, buttons = get_single_word_payload()
        else:
            text, buttons = get_chunk_payload()

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
