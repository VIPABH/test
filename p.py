from telethon import TelegramClient, events, errors, functions
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

# دالة لتحويل قائمة أرقام الصلاحيات إلى صلاحيات مشرف مركبة
def get_admin_rights_from_numbers(numbers: str) -> ChatAdminRights:
    return ChatAdminRights(
        change_info = '5' in numbers,
        post_messages = '7' in numbers,
        edit_messages = '6' in numbers,
        delete_messages = '1' in numbers,
        ban_users = '2' in numbers,
        invite_users = '3' in numbers,
        pin_messages = '4' in numbers,
        add_admins = False,
    )

@client.on(events.NewMessage(pattern=r'^رفع (\d+)$'))
async def raise_permissions(event):
    if not event.is_reply:
        await event.reply("الرجاء الرد على رسالة المستخدم الذي تريد رفعه ومنحه الصلاحيات.")
        return

    try:
        chat = await event.get_chat()
        sender = await event.get_sender()
        participant = await client(functions.channels.GetParticipantRequest(
            channel=chat,
            participant=sender
        ))
        admin_rights = getattr(participant.participant, 'admin_rights', None)
        if admin_rights is None or not admin_rights.add_admins:
            await event.reply("ليس لديك صلاحية رفع مشرفين.")
            return
    except errors.RPCError:
        await event.reply("حدث خطأ أثناء التحقق من الصلاحيات.")
        return

    numbers = event.pattern_match.group(1)
    for ch in numbers:
        if ch not in '1234567':
            await event.reply("الرجاء استخدام أرقام صلاحيات من 1 إلى 7 فقط.")
            return

    rights = get_admin_rights_from_numbers(numbers)
    replied_msg = await event.get_reply_message()
    user_to_promote = replied_msg.from_id

    try:
        await client(EditAdminRequest(
            channel=chat,
            user_id=user_to_promote,
            admin_rights=rights,
            rank="مشرف"
        ))
        await event.reply(f"تم رفع المستخدم ومنحه الصلاحيات: {', '.join(numbers)} بنجاح.")
    except errors.RPCError as e:
        await event.reply(f"فشل في رفع المشرف: {str(e)}")

client.run_until_disconnected()
