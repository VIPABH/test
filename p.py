import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# إعداد الاتصال
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "session"

# آيدي الشخص المسموح له استخدام الأمر
AUTHORIZED_USER_ID = int(os.getenv("OWNER_ID", "1910015590"))  # خزّنه كمتغير بيئة أو غيره يدويًا

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(pattern=r'^/react\s+(\S+)\s+(\d+)$'))
async def handler(event):
    # التحقق من المصرّح له
    if event.sender_id != AUTHORIZED_USER_ID:
        await event.reply("أنت غير مصرح لك باستخدام هذا الأمر.")
        return

    # فقط في المجموعات
    if not event.is_group:
        await event.reply("هذا الأمر يعمل فقط في المجموعات.")
        return

    # قراءة البيانات من الرسالة
    emoji = event.pattern_match.group(1)
    msg_id = int(event.pattern_match.group(2))

    try:
        await client(SendReactionRequest(
            peer=event.chat_id,
            msg_id=msg_id,
            reaction=[ReactionEmoji(emoticon=emoji)]
        ))
        await event.reply(f"تم التفاعل مع الرسالة {msg_id} بـ {emoji}")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء التفاعل: {str(e)}")

client.start()
print("Userbot is running...")
client.run_until_disconnected()
