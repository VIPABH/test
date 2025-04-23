import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji


API_ID_3 = os.getenv("API_ID_6")
API_HASH_3 = os.getenv("API_HASH_6")


if API_ID_3 and API_HASH_3:
    session_name = "session_6"
    client = TelegramClient(session_name, int(API_ID_3), API_HASH_3)

    target_user_id = None
    selected_emojis = []
print("✅ البوت جاهز. استخدم الأمر 'ازعاج + 🍓🍌🌟' بالرد على رسالة لتفعيل الإزعاج أو 'الغاء ازعاج' للإيقاف.")
