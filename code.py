"""
نظام Anti-Flood دقيق بالوقت لبوت Telethon
=============================================
الفكرة (مصححة):
- كل مستخدم عنده سجل بآخر أوقات رسائله (timestamps).
- نجمع آخر MAX_ATTEMPTS رسالة (مثلاً 5)، ونشوف الفرق الزمني الكلي
  بين أول رسالة وآخر رسالة بهالمجموعة.
- إذا هذا الفرق الكلي أقل من MIN_GAP ثانية (يعني 5 رسائل انبعتت
  خلال أقل من 3 ثواني) => فلود مؤكد.
- إذا الفرق الكلي 3 ثواني أو أكثر => طبيعي، حتى لو المستخدم يحچي
  بسرعة نسبياً، لأنه مو سريع بالشكل الآلي/المشبوه.

ملاحظة مهمة: هذا مختلف عن النسخة القديمة اللي كانت تشترط إن *كل*
فجوة بين كل رسالتين متتاليتين تكون أقل من 3 ثواني - هذا الشرط كان
صارم جداً وكان يسبب false positives (يقيّد ناس يحچون طبيعي بس
صدفة رسالتين منهم انبعتن قريبات من بعض).
"""

from ABH import ABH as client
from telethon import events
from collections import defaultdict
import time

# ------------------ الإعدادات ------------------
MAX_ATTEMPTS = 5          # عدد المحاولات المسموحة
MIN_GAP = 3.0             # أقل مدة كلية (بالثواني) لإرسال MAX_ATTEMPTS رسالة قبل ما تعتبر فلود
MUTE_DURATION = 60        # مدة الحظر المؤقت بالثواني بعد اكتشاف الفلود

# ------------------ تخزين البيانات ------------------
# لكل مستخدم: قائمة بأوقات آخر رسائله
user_timestamps = defaultdict(list)
# المستخدمين المحظورين مؤقتاً ووقت انتهاء الحظر
muted_users = {}


def is_flooding(user_id: int) -> bool:
    """
    يتحقق إذا المستخدم يسوي فلود سريع:
    - ياخذ آخر MAX_ATTEMPTS من الأوقات المسجلة.
    - يشوف الفرق الزمني الكلي من أول رسالة لآخر رسالة بهالمجموعة.
    - إذا هذا الفرق أقل من MIN_GAP ثانية => فلود (5 رسائل بأقل من 3 ثواني).
    - إذا 3 ثواني أو أكثر => طبيعي.
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

    # الفرق الزمني الكلي بين أول وآخر رسالة بالنافذة الحالية
    total_span = timestamps[-1] - timestamps[0]

    if total_span < MIN_GAP:
        # يعني MAX_ATTEMPTS رسالة انبعتت خلال أقل من MIN_GAP ثانية => فلود
        return True

    # الفرق 3 ثواني أو أكثر => طبيعي، مو فلود
    return False


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
        #muted_users[user_id] = time.time() + MUTE_DURATION
        user_timestamps[user_id].clear()  # نصفر السجل#

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


print("Anti-flood handler loaded.")
# ملاحظة: ما نستدعي client.run_until_disconnected() هنا لأن الكلاينت
# (ABH) غالباً يتم تشغيله من ملف رئيسي ثاني بالمشروع (main.py مثلاً).
# إذا هذا الملف هو نقطة التشغيل الوحيدة عندك، فك التعليق عن السطر التالي:
# client.run_until_disconnected()
