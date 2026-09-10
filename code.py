import asyncio
import re
import warnings

warnings.filterwarnings("ignore")

from ABH import ABH as client
import joblib
from Resources import *

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


def check_profanity(text: str) -> tuple[bool, float, str]:
    """دالة فحص النص: تعيد (هل بذيء، نسبة الثقة، السبب)"""
    if not text:
        return False, 0.0, "نص فارغ"

    # تفكيك النص لكلمات
    words = re.findall(r"\w+", text.lower())

    # الفحص الأول: المطابقة التامة المباشرة (100% دقة)
    for word in words:
        if word in BANNED_SET:
            return True, 1.0, f"كلمة محظورة: '{word}'"

    # الفحص الثاني: الموديل الذكي
    prob = model.predict_proba([text])[0][1]
    if prob >= 0.50:
        return True, prob, "تكهن الموديل الذكي"

    return False, prob, "نص سليم"


@client.on(events.NewMessage)
async def monitor_messages(event):
    # تجاهل الرسائل الفارغة أو الرسائل القادمة من البوتات
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text = event.raw_text
    if not text:
        return

    # فحص الكلمات البذيئة
    is_bad, confidence, reason = check_profanity(text)

    if is_bad:
        try:
            # 1. استخراج رابط الرسالة المباشر (Public أو Private)
            chat = await event.get_chat()
            if getattr(chat, "username", None):
                msg_link = f"https://t.me/{chat.username}/{event.id}"
            else:
                # للمجموعات والجروبات الخاصة
                clean_chat_id = str(event.chat_id).replace("-100", "")
                msg_link = f"https://t.me/c/{clean_chat_id}/{event.id}"

            # 2. جمع معلومات المرسل
            first_name = sender.first_name or "بدون اسم"
            last_name = f" {sender.last_name}" if sender.last_name else ""
            full_name = f"{first_name}{last_name}"
            username = f"@{sender.username}" if sender.username else "لا يوجد"
            user_id = sender.id

            # 3. صياغة التقرير الإشعاري
            report_text = (
                f"🚨 **تم كشف كلام بذيء!**\n\n"
                f"👤 **معلومات المرسل:**\n"
                f"• **الاسم:** [{full_name}](tg://user?id={user_id})\n"
                f"• **اليوزر:** {username}\n"
                f"• **الآيدي:** `{user_id}`\n\n"
                f"📝 **النص المخالف:**\n`{text}`\n\n"
                f"🔍 **السبب / الكلمة:** `{reason}`\n"
                f"📊 **نسبة الثقة:** `{confidence * 100:.1f}%`\n\n"
                f"🔗 **رابط الرسالة:** [اضغط هنا للانتثال للرسالة]({msg_link})"
            )

            # إرسال التقرير لجهة الاستلام المحددة (wfffp)
            await client.send_message(
                wfffp, report_text, link_preview=False
            )


        except Exception as e:
            print(f"خطأ أثناء إرسال التقرير: {e}")
