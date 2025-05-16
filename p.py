from telethon import TelegramClient, events, errors, functions
from telethon.tl.functions.channels import EditAdminRequest, GetParticipantRequest
from telethon.tl.types import ChatAdminRights
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

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

    chat = await event.get_chat()
    sender = await event.get_sender()
    replied_msg = await event.get_reply_message()
    user_to_promote = replied_msg.sender_id

    # التحقق من صلاحيات المرسل لرفع مشرفين
    try:
        participant = await client(GetParticipantRequest(
            channel=chat,
            participant=sender.id
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

    new_rights = get_admin_rights_from_numbers(numbers)

    # جلب صلاحيات المستخدم الحالي (إن كان مشرف)
    try:
        participant_to_promote = await client(GetParticipantRequest(
            channel=chat,
            participant=user_to_promote
        ))
        current_rights = getattr(participant_to_promote.participant, 'admin_rights', ChatAdminRights())
    except errors.RPCError:
        # إذا لم يكن مشرفًا سابقًا نعتبر الصلاحيات فارغة
        current_rights = ChatAdminRights()

    # دمج الصلاحيات القديمة مع الجديدة (إضافة فقط)
    merged_rights = ChatAdminRights(
        change_info = current_rights.change_info or new_rights.change_info,
        post_messages = current_rights.post_messages or new_rights.post_messages,
        edit_messages = current_rights.edit_messages or new_rights.edit_messages,
        delete_messages = current_rights.delete_messages or new_rights.delete_messages,
        ban_users = current_rights.ban_users or new_rights.ban_users,
        invite_users = current_rights.invite_users or new_rights.invite_users,
        pin_messages = current_rights.pin_messages or new_rights.pin_messages,
        add_admins = current_rights.add_admins or new_rights.add_admins,
        manage_invite_links = getattr(current_rights, 'manage_invite_links', False) or getattr(new_rights, 'manage_invite_links', False),
        post_stories = getattr(current_rights, 'post_stories', False) or getattr(new_rights, 'post_stories', False),
        edit_stories = getattr(current_rights, 'edit_stories', False) or getattr(new_rights, 'edit_stories', False),
        delete_stories = getattr(current_rights, 'delete_stories', False) or getattr(new_rights, 'delete_stories', False),
        manage_call = getattr(current_rights, 'manage_call', False) or getattr(new_rights, 'manage_call', False),
    )

    try:
        await client(EditAdminRequest(
            channel=chat,
            user_id=user_to_promote,
            admin_rights=merged_rights,
            rank="مشرف"
        ))
        await event.reply(f"تم رفع المستخدم ومنحه الصلاحيات: {', '.join(numbers)} مع الحفاظ على الصلاحيات السابقة.")
    except errors.RPCError as e:
        await event.reply(f"فشل في رفع المشرف: {str(e)}")

client.run_until_disconnected()
