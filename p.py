from telethon import TelegramClient, events
import os, requests


# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def date(user_id):
    headers = {
        'Host': 'restore-access.indream.app',
        'Connection': 'keep-alive',
        'x-api-key': 'e758fb28-79be-4d1c-af6b-066633ded128',
        'Accept': '*/*',
        'Accept-Language': 'ar',
        'Content-Length': '25',
        'User-Agent': 'Nicegram/101 CFNetwork/1404.0.5 Darwin/22.3.0',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = '{"telegramId":' + str(user_id) + '}'
    response = requests.post('https://restore-access.indream.app/regdate', headers=headers, data=data).json()
    zelzal_date = response['data']['date']
    return zelzal_date

LOCAL_PHOTO_DIR = "photos"
os.makedirs(LOCAL_PHOTO_DIR, exist_ok=True)

@ABH.on(events.NewMessage(pattern=r'id', forwards=False))
async def handler(event):
    try:
        if event.is_reply:
            replied_message = await event.get_reply_message()
            sender_id = replied_message.sender_id
        else:
            sender_id = event.sender_id
        
        user = await ABH.get_entity(sender_id)
        
        user_id = user.id
        phone = user.phone if hasattr(user, 'phone') else "—"
        premium = "yes" if user.premium else "no"
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["x04ou"]
        usernames_list = ", ".join(usernames)
        bio = user.about if user.about else "🙄"
        account_creation_date = await date(user_id)
        message_text = (
            f"𖡋 𝐔𝐒𝐄 ⌯ {usernames_list}\n"
            f"𖡋 𝐢𝐬𝐩 ⌯ {premium}\n"
            f"𖡋 𝐏𝐇𝐍 ⌯ {phone}\n"
            f"𖡋 𝐁𝐈𝐎 ⌯ {bio}\n"
            f"𖡋 𝐂𝐑 ⌯ {account_creation_date}\n"
        )
        if user.photo:
            photo_path = os.path.join(LOCAL_PHOTO_DIR, f"{user_id}.jpg")
            await ABH.download_profile_photo(user.id, file=photo_path)
            await ABH.send_file(
                event.chat_id,
                photo_path,
                caption=message_text,
                force_document=False
            )
        else:
            await event.respond(message_text)
    
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
