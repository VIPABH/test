from ABH import ABH as client
"""
نظام Anti-Flood دقيق بالوقت لبوت Telethon
=============================================
الفكرة:
- كل مستخدم عنده سجل بآخر أوقات رسائله (timestamps).
- إذا صار عنده 5 رسائل متتالية وكل فجوة زمنية بينها أقل من 3 ثواني
  => يعتبر "فلود" ويتم كشفه واتخاذ إجراء.
- إذا الفجوات بين الرسائل أكثر من 3 ثواني، ما يُحسب فلود حتى لو
  كرر نفس عدد الرسائل، لأنه "طبيعي" مو سريع.

يعني الشرط الدقيق:
  عدد المحاولات (MAX_ATTEMPTS) خلال فترة كل فجوة بينها أقل من
  MIN_GAP ثانية.
"""

from telethon import TelegramClient, events
from collections import defaultdict
import time

# ------------------ الإعدادات ------------------
API_ID = 123456          # عوّضها بـ API ID تبعك
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

MAX_ATTEMPTS = 5          # عدد المحاولات المسموحة
MIN_GAP = 3.0             # أقل فجوة زمنية مسموحة (بالثواني) بين رسالتين متتاليتين
MUTE_DURATION = 60        # مدة الحظر المؤقت بالثواني بعد اكتشاف الفلود

# ------------------ تخزين البيانات ------------------
# لكل مستخدم: قائمة بأوقات آخر رسائله
user_timestamps = defaultdict(list)
# المستخدمين المحظورين مؤقتاً ووقت انتهاء الحظر
muted_users = {}

#client = TelegramClient("anti_flood_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


def is_flooding(user_id: int) -> bool:
    """
    يتحقق إذا المستخدم يسوي فلود سريع:
    - ياخذ آخر MAX_ATTEMPTS من الأوقات المسجلة.
    - يشوف إذا كل الفجوات بينها أقل من MIN_GAP ثانية.
    """
    now = time.time()
    timestamps = user_timestamps[user_id]

    # نضيف الوقت الحالي للسجل
    timestamps.append(now)

    # نحتفظ فقط بآخر MAX_ATTEMPTS وقت (نحذف الأقدم)
    if len(timestamps) > MAX_ATTEMPTS:
        timestamps.pop(0)

    # إذا ما وصلنا للعدد المطلوب بعد، مو فلود
    if len(timestamps) < MAX_ATTEMPTS:
        return False

    # نتحقق: هل كل فجوة بين رسالتين متتاليتين أقل من MIN_GAP؟
    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap >= MIN_GAP:
            # لقينا فجوة طبيعية (أكثر من 3 ثواني) => مو فلود
            return False

    # كل الفجوات كانت أقل من MIN_GAP => فلود مؤكد
    return True


def is_muted(user_id: int) -> bool:
    """يتحقق إذا المستخدم بفترة حظر مؤقت حالياً."""
    if user_id in muted_users:
        if time.time() < muted_users[user_id]:
            return True
        else:
            # انتهت مدة الحظر
            del muted_users[user_id]
    return False


@client.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id

    # تجاهل رسائل البوتات نفسها لو موجودة بالمجموعة
    if event.sender and getattr(event.sender, "bot", False):
        return

    # تحقق أول إذا المستخدم محظور مؤقتاً
    if is_muted(user_id):
        await event.delete()  # يحذف رسائله وهو بفترة الحظر
        return

    # تحقق من الفلود
    if is_flooding(user_id):
        # اكتشفنا فلود -> نطبق الإجراء
        muted_users[user_id] = time.time() + MUTE_DURATION
        user_timestamps[user_id].clear()  # نصفر السجل

        try:
            await event.reply(
                f"⚠️ تم رصد فلود من طرفك. تم تقييدك لمدة {MUTE_DURATION} ثانية."
            )
        except Exception:
            pass

        # هنا تكدر تضيف: طرد، حظر بالمجموعة، تسجيل بقاعدة بيانات، ...
        # مثال حظر فعلي بالمجموعة (لازم البوت يكون أدمن):
        #
        # from telethon.tl.functions.channels import EditBannedRequest
        # from telethon.tl.types import ChatBannedRights
        # await client(EditBannedRequest(
        #     event.chat_id, user_id,
        #     ChatBannedRights(until_date=int(time.time() + MUTE_DURATION), send_messages=True)
        # ))
        return

    # إذا وصلنا لهنا، الرسالة طبيعية وما راح نسوي شي


print("Anti-flood bot is running...")
