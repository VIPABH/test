from telethon import events
from ABH import *
import json
import os

# تابع لتحديد نوع الرسالة
def get_message_type(msg):
    # مثال مبسط: يمكنك استخدام دالتك السابقة هنا
    if msg.message and not msg.media:
        return "text"
    if msg.media:
        # فحص الفيديو/فويس/GIF كما سبق
        if hasattr(msg.media, 'document') and msg.media.document:
            for attr in msg.media.document.attributes:
                from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo, DocumentAttributeAnimated
                if isinstance(attr, DocumentAttributeAudio):
                    return "voice" if not getattr(attr, "voice", False) else "voice note"
                if isinstance(attr, DocumentAttributeVideo):
                    if getattr(attr, "round_message", False):
                        return "voice note"
                    if getattr(attr, "audio", None) is None:
                        return "gif"
                    return "video"
                if isinstance(attr, DocumentAttributeAnimated):
                    return "gif"
    return "other"  # fallback لأي نوع آخر

# دالة لتحديث JSON
async def info(e, msg_type):
    f = 'info.json'

    # إنشاء الملف إذا لم يكن موجود
    if not os.path.exists(f):
        with open(f, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)

    chat = str(e.chat_id)
    user_id = str(e.sender_id)

    if chat not in data:
        data[chat] = {}
    if user_id not in data[chat]:
        data[chat][user_id] = {}

    if msg_type not in data[chat][user_id]:
        data[chat][user_id][msg_type] = 0
    data[chat][user_id][msg_type] += 1

    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return data[chat][user_id]

# الحدث الرئيسي للبوت
@ABH.on(events.NewMessage)
async def track_messages(e):
    m = e.message
    msg_type = get_message_type(m)

    # تحديث الإحصائيات تلقائيًا
    user_stats = await info(e, msg_type)

    # إذا كتب المستخدم "مع" يتم إرسال التقرير
    if m.text == "مع":
        import json
        stats_str = json.dumps(user_stats, ensure_ascii=False, indent=2)
        await e.reply(f"إحصائياتك حتى الآن:\n{stats_str}")
