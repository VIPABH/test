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
    "edit": ("change_info", "تعديل معلومات المجموعة"),
    "ban": ("ban_users", "حظر المستخدمين"),
    "delete": ("delete_messages", "حذف الرسائل"),
    "pin": ("pin_messages", "تثبيت الرسائل"),
    "invite": ("invite_users", "دعوة مستخدمين"),
    "invite_link": ("manage_invite_links", "إدارة الدعوات"),
    "calls": ("manage_call", "صلاحيات الاتصال"),
    "add_admins": ("add_admins", "تعيين مشرفين"),
    "stories": (["post_stories", "edit_stories", "delete_stories"], "إدارة الستوري"),
}

buttons_layout = [
    ["edit", "ban"], ["delete", "pin"], ["invite", "invite_link"],
    ["stories", "calls"], ["add_admins"], ["promote", "cancel"]
]

@bot.on(events.NewMessage(pattern="^ر$"))
async def assign_permissions(event):
    if not event.is_reply:
        return await event.reply("يرجى الرد على رسالة المستخدم الذي تريد رفعه.")

    reply = await event.get_reply_message()
    admin_sessions[event.sender_id] = {
        "target_id": reply.sender_id,
        "rights": ChatAdminRights()
    }

    def make_label(key):
        if key in rights_map:
            return f"✔️ {rights_map[key][1]}"
        return "✅ تنفيذ" if key == "promote" else "❌ إلغاء"

    buttons = [[Button.inline(make_label(b), b.encode()) for b in row] for row in buttons_layout]

    await event.reply("اختر الصلاحيات التي تريد منحها للمستخدم:", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender, chat = event.sender_id, event.chat_id
    session = admin_sessions.get(sender)

    if not session:
        return await event.answer("انتهت الجلسة أو غير مصرح لك.", alert=True)

    data = event.data.decode()
    if data == "cancel":
        admin_sessions.pop(sender, None)
        return await event.edit("❌ تم إلغاء العملية.")

    if data == "promote":
        session = admin_sessions.pop(sender)
        rights, target_id = session['rights'], session['target_id']

        try:
            await bot(EditAdminRequest(channel=chat, user_id=target_id, admin_rights=rights, rank="مشرف"))
            granted = [
                name for key, (attr, name) in rights_map.items()
                if isinstance(attr, list) and any(getattr(rights, a, False) for a in attr) or
                   isinstance(attr, str) and getattr(rights, attr, False)
            ]
            desc = "\n• " + "\n• ".join(granted) if granted else "بدون صلاحيات مذكورة"
            return await event.edit(f"✅ تم رفع المستخدم مشرفًا بالصلاحيات التالية:\n{desc}",
                                    buttons=[Button.inline("✏️ تغيير اللقب", f"change_nick:{target_id}".encode())])
        except Exception as e:
            return await event.edit(f"❌ حدث خطأ أثناء التنفيذ:\n{e}")

    rights = session["rights"]
    attr, msg = rights_map.get(data, (None, None))
    if not attr:
        return

    if isinstance(attr, list):
        for a in attr:
            setattr(rights, a, True)
    else:
        setattr(rights, attr, True)

    await event.answer(f"✔️ تم تفعيل: {msg}")

@bot.on(events.CallbackQuery(pattern=b"change_nick:(\\d+)"))
async def change_nickname(event):
    target_id = int(event.pattern_match.group(1))
    admin_sessions[event.sender_id] = {"target_id": target_id}
    await event.respond("✏️ أرسل اللقب الجديد في رسالة عادية الآن.")

bot.run_until_disconnected()
