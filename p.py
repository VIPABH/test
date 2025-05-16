from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

admin_sessions = {}

rights_map = {
    "edit": ("تعديل معلومات المجموعة", "change_info"),
    "ban": ("حظر المستخدمين", "ban_users"),
    "delete": ("حذف الرسائل", "delete_messages"),
    "pin": ("تثبيت الرسائل", "pin_messages"),
    "invite": ("دعوة مستخدمين", "invite_users"),
    "invite_link": ("إدارة الدعوات", "manage_invite_links"),
    "stories": ("إدارة الستوري", ["post_stories", "edit_stories", "delete_stories"]),
    "calls": ("صلاحيات الاتصال", "manage_call"),
    "add_admins": ("تعيين مشرفين", "add_admins"),
}

@bot.on(events.NewMessage(pattern="^ر$"))
async def assign_permissions(event):
    if not event.is_reply:
        return await event.reply("يرجى الرد على رسالة المستخدم الذي تريد رفعه.")

    reply = await event.get_reply_message()
    admin_sessions[event.sender_id] = {
        "target_id": reply.sender_id,
        "rights": ChatAdminRights()
    }

    buttons = [
        [Button.inline(name, key.encode()) for key, (name, _) in list(rights_map.items())[i:i+2]]
        for i in range(0, len(rights_map), 2)
    ] + [[Button.inline("✅ تنفيذ", b"promote"), Button.inline("❌ إلغاء", b"cancel")]]
    
    await event.reply("اختر الصلاحيات التي تريد منحها للمستخدم:", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = event.sender_id
    session = admin_sessions.get(sender)
    if not session:
        return await event.answer("انتهت الجلسة أو غير مصرح لك.", alert=True)

    data = event.data.decode()
    chat = event.chat_id
    rights = session["rights"]

    if data == "cancel":
        admin_sessions.pop(sender, None)
        return await event.edit("❌ تم إلغاء العملية.")

    if data == "promote":
        session = admin_sessions.pop(sender)
        target_id, rights = session["target_id"], session["rights"]

        try:
            await bot(EditAdminRequest(chat, target_id, rights, rank="مشرف"))
            granted = [name for key, (name, attr) in rights_map.items()
                       if isinstance(attr, list)
                       and any(getattr(rights, a, False) for a in attr)
                       or getattr(rights, attr if isinstance(attr, str) else "", False)]

            desc = "\n• " + "\n• ".join(granted) if granted else "بدون صلاحيات مذكورة"
            await event.edit(f"✅ تم رفع المستخدم مشرفًا بالصلاحيات التالية:\n{desc}",
                             buttons=[Button.inline("✏️ تغيير اللقب", f"change_nick:{target_id}".encode())])
        except Exception as e:
            await event.edit(f"❌ حدث خطأ أثناء التنفيذ:\n{e}")
        return

    if data in rights_map:
        name, attr = rights_map[data]
        if isinstance(attr, list):
            for a in attr:
                setattr(rights, a, True)
        else:
            setattr(rights, attr, True)
        await event.answer(f"✔️ تم تفعيل: {name}")

@bot.on(events.CallbackQuery(pattern=b"change_nick:(\\d+)"))
async def change_nickname(event):
    target_id = int(event.pattern_match.group(1))
    admin_sessions[event.sender_id] = {"target_id": target_id}
    await event.respond("✏️ أرسل اللقب الجديد في رسالة عادية الآن.")

bot.run_until_disconnected()
