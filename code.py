import asyncio
import re
import warnings

warnings.filterwarnings("ignore")

from ABH import ABH as client
import joblib
from Resources import *



import json
import re
from datetime import datetime


# Set لمنع التكرار تلقائياً
sentences = set()


@client.on(events.NewMessage)
async def handler(event):
    global sentences

    if not event.raw_text:
        return

    # تقسيم النص إلى جمل حسب الأسطر وعلامات الترقيم
    split_sentences = re.split(r"[\n.!?؟]+", event.raw_text)

    for s in split_sentences:
        text = s.strip()
        if len(text) > 3:  # تجاهل الرموز والكلمات القصيرة جداً
            sentences.add(text)

    # عند الوصول إلى 1000 جملة
    if len(sentences) >= 1000:
        data_to_save = list(sentences)[:1000]

        # حفظ الملف
        filename = f"sentences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        # إرسال الملف والإشعار إلى الرسائل المحفوظة
        await client.send_file(
            wfffp,
            filename,
            caption=f"✅ تم جمع وحفظ {len(data_to_save)} جملة بنجاح!",
        )

        # إعادة تصفير الـ Set للدفعة القادمة
        sentences.clear()



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
