from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# إعدادات البوت
api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# معرف القناة (public username)
channel_username = 'x04ou'  # بدون @

@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    user_id = event.sender_id

    try:
        # التحقق من العضوية
        await client(GetParticipantRequest(channel_username, user_id))
        
        # في حال كان مشترك
        await event.respond("مرحبًا بك، يمكنك استخدام البوت ✅")
    
    except UserNotParticipantError:
        # في حال لم يكن مشتركًا
        await event.respond(
            f"🚫 للاستخدام، يجب الاشتراك أولًا في القناة:\n"
            f"👉 https://t.me/{channel_username}\n"
            f"ثم أرسل /start مجددًا."
        )

client.run_until_disconnected()
