import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# إعداد الاتصال
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "session"

# آيدي المستخدم المستهدف
TARGET_USER_ID = 6505528233  # يمكنك تغييره لمستخدم آخر
DEFAULT_EMOJI = os.getenv("DEFAULT_REACT", "🍌")  # يمكنك تغييره من متغير بيئة

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage())
async def auto_react(event):
    # التأكد أن المرسل هو الشخص المطلوب
    if event.sender_id == TARGET_USER_ID:
        try:
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[ReactionEmoji(emoticon=DEFAULT_EMOJI)]
            ))
            print(f"Reacted to message {event.id} from target user.")
        except Exception as e:
            print(f"فشل التفاعل مع الرسالة {event.id}: {e}")

client.start()
print("Userbot is running and listening for target user's messages...")
client.run_until_disconnected()
