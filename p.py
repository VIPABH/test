from telethon import TelegramClient, events
import os
import aiohttp
from datetime import datetime
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.users import GetFullUserRequest

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# مجلد الصور المحلية
LOCAL_PHOTO_DIR = "photos"
os.makedirs(LOCAL_PHOTO_DIR, exist_ok=True)

# دالة لجلب تاريخ التسجيل
async def date(user_id):
    headers = {
        'Host': 'restore-access.indream.app',
        'Connection': 'keep-alive',
        'x-api-key': 'e758fb28-79be-4d1c-af6b-066633ded128',
        'Accept': '*/*',
        'Accept-Language': 'ar',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Nicegram/101 CFNetwork/1404.0.5 Darwin/22.3.0',
    }
    data = '{"telegramId":' + str(user_id) + '}'
    
    async with aiohttp.ClientSession() as session:
        async with session.post('https://restore-access.indream.app/regdate', headers=headers, data=data) as response:
            response_json = await response.json()
            date_string = response_json['data']['date']
            date_obj = datetime.strptime(date_string, "%Y-%m")
            formatted_date = date_obj.strftime("%Y/%m")
            return formatted_date

# دالة لجلب دور المستخدم في المجموعة
async def get_user_role(user_id, chat_id):
    participant = await ABH.get_participant(chat_id, user_id)

    if isinstance(participant, ChannelParticipantCreator):
        return "مالك"
    elif isinstance(participant, ChannelParticipantAdmin):
        return "مشرف"
    elif isinstance(participant, ChannelParticipant):
        return "عضو"
    else:
        return "غير معروف"

# الدالة التي تستجيب للرسائل
@ABH.on(events.NewMessage(pattern=r'id', forwards=False))
async def handler(event):
    try:
        # التحقق إذا كان الرد على رسالة
        if event.is_reply:
            replied_message = await event.get_reply_message()
            sender_id = replied_message.sender_id
        else:
            sender_id = event.sender_id
        
        user = await ABH.get_entity(sender_id)
        
        user_id = user.id
        chat_id = event.chat_id
        phone = user.phone if hasattr(user, 'phone') and user.phone else "—"
        premium = "yes" if user.premium else "no"
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["x04ou"]
        usernames_list = ", ".join(usernames)
        dates = await date(user_id)
        # full = await ABH(GetFullUserRequest(user.id))
        # bio = full.user.about if hasattr(full.user, 'about') and full.user.about else "🙄"
        states = await get_user_role(user_id, chat_id)
        
        message_text = (
            f"𖡋 𝐔𝐒𝐄 ⌯ {usernames_list}\n"
            f"𖡋 𝐈𝐒𝐏 ⌯ {premium}\n"
            f"𖡋 𝐏𝐇𝐍 ⌯ {'+' + phone if phone != '—' else phone}\n"
            f"𖡋 𝐂𝐑 ⌯ {dates}\n"
            f"𖡋 𝐑𝐎𝐋𝐄 ⌯ {states}\n"
            # f"{bio}\n"
        )

        # إذا كان هناك صورة للمستخدم
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
