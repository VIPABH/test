from telethon import TelegramClient, events
import os
import aiohttp  # type: ignore
from datetime import datetime
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantRequest
import io
from asyncio import gather

# إعداد بيانات البوت
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لجلب دور المستخدم داخل القناة
async def get_user_role(user_id, chat_id):
    try:
        result = await ABH(GetParticipantRequest(
            channel=chat_id,
            participant=user_id
        ))
        participant = result.participant

        if isinstance(participant, ChannelParticipantCreator):
            return "مالك"
        elif isinstance(participant, ChannelParticipantAdmin):
            return "مشرف"
        elif isinstance(participant, ChannelParticipant):
            return "عضو"
        else:
            return "غير معروف"
    except Exception as e:
        return f"خطأ في الحصول على الدور: {e}"

# دالة لجلب تاريخ إنشاء الحساب
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
                date_obj = datetime.strptime(date_string, "%Y-%m")
                formatted_date = date_obj.strftime("%Y/%m")
                return formatted_date
            else:
                return "غير معروف"

# الحدث عند إرسال "ايدي"
@ABH.on(events.NewMessage(pattern='id|ا|افتاري|ايدي'))
async def handler(event):
    try:
        if event.is_reply:
            replied_message = await event.get_reply_message()
            sender_id = replied_message.sender_id
        else:
            sender_id = event.sender_id

        user = await ABH.get_entity(sender_id)
        user_id = user.id
        chat_id = event.chat_id

        phone = user.phone if hasattr(user, 'phone') and user.phone else "—"
        premium = "yes" if getattr(user, 'premium', False) else "no"
        usernames = [f"@{username.username}" for username in user.usernames] if getattr(user, 'usernames', None) else ["x04ou"]
        usernames_list = ", ".join(usernames)

        # تنفيذ المهام البطيئة بالتوازي
        dates_task, role_task, full_user_task = await gather(
            date(user_id),
            get_user_role(user_id, chat_id),
            ABH(GetFullUserRequest(user.id))
        )
        dates = dates_task
        states = role_task
        FullUser = full_user_task
        bio = FullUser.full_user.about or ""

        message_text = (
            f"𖡋 𝐔𝐒𝐄 ⌯ {usernames_list}\n"
            f"𖡋 𝐈𝐒𝐏 ⌯ {premium}\n"
            f"𖡋 𝐏𝐇𝐍 ⌯ {'+' + phone if phone != '—' else phone}\n"
            f"𖡋 𝐂𝐑 ⌯ {dates}\n"
            f"𖡋 𝐑𝐎𝐋𝐄 ⌯ {states}\n"
            f"{bio}"
        )

        # إرسال صورة البروفايل إذا كانت موجودة
        if user.photo:
            photo = await ABH.download_profile_photo(user.id, file=bytes)
            await ABH.send_file(
                event.chat_id,
                file=io.BytesIO(photo),
                caption=message_text,
                force_document=False
            )
        else:
            await event.respond(message_text)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
