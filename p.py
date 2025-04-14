from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

rights_translation = {
    "change_info": "تغيير معلومات المجموعة",
    "post_messages": "نشر الرسائل",
    "edit_messages": "تعديل الرسائل",
    "delete_messages": "حذف الرسائل",
    "ban_users": "حظر الأعضاء",
    "invite_users": "دعوة أعضاء",
    "pin_messages": "تثبيت الرسائل",
    "add_admins": "إضافة مشرفين",
    "manage_call": "إدارة المكالمات الصوتية",
    "anonymous": "الوضع المتخفي",
    "manage_topics": "إدارة المواضيع",
}

def translate_rights_lines(rights_obj):
    lines = []
    for key, name in rights_translation.items():
        status = getattr(rights_obj, key, False)
        emoji = "👍🏾" if status else "👎🏾"
        lines.append(f"{name} ⇜ {emoji}")
    return "\n".join(lines) if lines else "لا يوجد صلاحيات"

@ABH.on(events.NewMessage(pattern='صلاحياتي'))
async def my_rights(event):
    try:
        chat = await event.get_input_chat()
        sender_id = event.sender_id
        result = await ABH(GetParticipantRequest(channel=chat, participant=sender_id))
        translated = translate_rights_lines(result.participant.admin_rights)
        await event.reply(f"صلاحياتك:\n{translated}")
    except Exception:
        await event.reply("لا يمكن عرض الصلاحيات.")

@ABH.on(events.NewMessage(pattern='صلاحياته'))
async def his_rights(event):
    try:
        msg = await event.get_reply_message()
        if not msg:
            await event.reply("رد على رسالة المستخدم أولًا.")
            return
        chat = await event.get_input_chat()
        sender_id = msg.sender_id
        result = await ABH(GetParticipantRequest(channel=chat, participant=sender_id))
        translated = translate_rights_lines(result.participant.admin_rights)
        await event.reply(f"صلاحياته:\n{translated}")
    except Exception:
        await event.reply("لا يمكن عرض الصلاحيات.")

ABH.start()
ABH.run_until_disconnected()
