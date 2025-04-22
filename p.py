import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# إعداد الاتصال
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "session"

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(pattern='ازعاج'))
async def auto_react(event):
    TARGET_USER_ID = event.sender_id
    x = "🍌"  # اختر رمز تعبيري مخصص بدلاً من استخدام نص الرسالة
    if event.sender_id == TARGET_USER_ID:
        try:
            # إرسال التفاعل باستخدام رمز تعبيري مخصص
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[ReactionEmoji(emoticon=x)]  # رمز تعبيري مخصص
            ))
            print(f"Reacted to message {event.id} from target user.")
        except Exception as e:
            print(f"فشل التفاعل مع الرسالة {event.id}: {e}")

client.start()
print("Userbot is running and listening for target user's messages...")
client.run_until_disconnected()
