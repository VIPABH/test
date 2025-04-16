from telethon import TelegramClient, events
import os, asyncio
import aiohttp #type: ignore
from datetime import datetime
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator, Channel
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantRequest
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
LOCAL_PHOTO_DIR = "photos"
os.makedirs(LOCAL_PHOTO_DIR, exist_ok=True)
async def get_user_role(user_id, chat_id):
    try:
        chat = await ABH.get_entity(chat_id)
        if isinstance(chat, Channel):
            result = await ABH(GetParticipantRequest(channel=chat, participant=user_id))
            participant = result.participant

            if isinstance(participant, ChannelParticipantCreator):
                return "مالك"
            elif isinstance(participant, ChannelParticipantAdmin):
                return "مشرف"
            elif isinstance(participant, ChannelParticipant):
                return "عضو"
            else:
                return ''
        else:
            return ''

    except Exception:
        return "🌚"
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
            if response.status == 200:
                response_json = await response.json()
                date_string = response_json['data']['date']
                try:
                    if len(date_string.split("-")) == 3:
                        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%Y/%m/%d")
                    else:
                        date_obj = datetime.strptime(date_string, "%Y-%m")
                        formatted_date = date_obj.strftime("%Y/%m")
                    return formatted_date
                except Exception:
                    return "تاريخ غير صالح"
            else:
                return "غير معروف"
LOCAL_PHOTO_DIR = "/tmp"

@ABH.on(events.NewMessage(pattern='^(id|ا|افتاري|ايدي)$'))
async def handler(event):
    if event.is_private:
        return
    sender_id = event.sender_id
    user = await ABH.get_entity(sender_id)
    user_id = user.id
    chat_id = event.chat_id
    phone = user.phone if hasattr(user, 'phone') and user.phone else "😶"
    premium = "yes" if user.premium else "no"
    usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else [f"@{user.username}"] if user.username else ["—"]
    usernames_list = ", ".join(usernames)
    dates = await date(user_id)
    states = await get_user_role(user_id, chat_id)
    FullUser = (await event.client(GetFullUserRequest(user.id))).full_user
    bio = FullUser.about
    bio_text = f"\n{bio}" if bio and bio.strip() else ""
    message_text = (
        f"𖡋 𝐔𝐒𝐄 ⌯ {usernames_list}\n"
        f"𖡋 𝐈𝐒𝐏 ⌯ {premium}\n"
        f"𖡋 𝐏𝐇𝐍 ⌯ {'+' + phone if phone != '—' else phone}\n"
        f"𖡋 𝐂𝐑 ⌯ {dates}\n"
        f"𖡋 𝐑𝐎𝐋𝐄 ⌯ {states}"
        f"{bio_text}"
    )
    if user.photo:
        photo_path = os.path.join(LOCAL_PHOTO_DIR, f"{user_id}.jpg")
        await ABH.download_profile_photo(user.id, file=photo_path)
        msg = await ABH.send_file(event.chat_id, photo_path, caption=message_text, force_document=False)
        await asyncio.sleep(60*3)
        await msg.delete()
    else:
        await event.respond(message_text)
@ABH.on(events.NewMessage(pattern='^(id|اا|افتار|ايدي)$'))
async def handler(event):
    if event.is_reply:
        replied_message = await event.get_reply_message()
        sender_id = replied_message.sender_id
    user = await ABH.get_entity(sender_id)
    user_id = user.id
    chat_id = event.chat_id
    phone = user.phone if hasattr(user, 'phone') and user.phone else "المستخدم لا يشارك رقم الهاتف"
    premium = "yes" if user.premium else "no"
    usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else [f"@{user.username}"] if user.username else ["—"]
    usernames_list = ", ".join(usernames)
    dates = await date(user_id)
    states = await get_user_role(user_id, chat_id)
    FullUser = (await event.client(GetFullUserRequest(user.id))).full_user
    bio = FullUser.about
    bio_text = f"\n{bio}" if bio and bio.strip() else ""
    message_text = (
        f"𖡋 𝐔𝐒𝐄 ⌯ {usernames_list}\n"
        f"𖡋 𝐈𝐒𝐏 ⌯ {premium}\n"
        f"𖡋 𝐏𝐇𝐍 ⌯ {'+' + phone if phone != '—' else phone}\n"
        f"𖡋 𝐂𝐑 ⌯ {dates}\n"
        f"𖡋 𝐑𝐎𝐋𝐄 ⌯ {states}"
        f"{bio_text}"
    )
    if user.photo:
        photo_path = os.path.join(LOCAL_PHOTO_DIR, f"{user_id}.jpg")
        await ABH.download_profile_photo(user.id, file=photo_path)
        msg = await ABH.send_file(event.chat_id, photo_path, caption=message_text, force_document=False)
        await asyncio.sleep(60*3)
        await msg.delete()
    else:
        await event.respond(message_text)
ABH.run_until_disconnected()
