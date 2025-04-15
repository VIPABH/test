from telethon import TelegramClient, events
import os

api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'id'))
async def handler(event):
    if event.is_reply:
        replied_message = await event.get_reply_message()
        sender_id = replied_message.sender_id
    else:
        sender_id = event.sender_id
        user = await ABH.get_entity(sender_id)        
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name if user.last_name else ''
        full_name = f"{first_name} {last_name}".strip()
        phone = user.phone if hasattr(user, 'phone') else "None"
        premium = "نعم" if user.premium else "لا"
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["—"]
        usernames_list = " ".join(usernames)  
        try:
            permissions = await ABH.get_permissions(event.chat_id, user_id)
            if permissions.is_creator:
                rank = "المالك"
            elif permissions.is_admin:
                rank = "مشرف"
            else:
                rank = "عضو"
        except:
            rank = "عضو"

        if user.photo:
            photo = await ABH.download_profile_photo(user.id)
        else:
            photo = None

        if photo:
            await event.respond(f"{user_id}\n{first_name}\n{premium}\n{full_name}\n{phone}\n{usernames_list}\nالرتبة: {rank}", file=photo, force_document=False
)
        else:
            await event.respond(f"{user_id}\n{first_name}\n{premium}\n{full_name}\n{phone}\n{usernames_list}\nالرتبة: {rank}")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
