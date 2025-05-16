from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

admin_sessions = {}

# الصلاحيات المتاحة مع أوصافها
rights_map = {
    "edit": ("change_info", "تعديل معلومات المجموعة"),
    "ban": ("ban_users", "حظر المستخدمين"),
    "delete": ("delete_messages", "حذف الرسائل"),
    "pin": ("pin_messages", "تثبيت الرسائل"),
    "invite": ("invite_users", "دعوة مستخدمين"),
    "invite_link": ("manage_invite_links", "إدارة الدعوات"),
    "stories": ("post_stories", "إدارة الستوري"),
    "calls": ("manage_call", "صلاحيات الاتصال"),
    "add_admins": ("add_admins", "تعيين مشرفين"),
}

buttons_layout = [
    ["edit", "ban"],
    ["delete", "pin"],
    ["invite", "invite_link"],
    ["stories", "calls"],
    ["add_admins"],
    ["promote", "cancel"],
]

@bot.on(events.NewMessage(pattern="^ر$"))
async def assign_permissions(event):
    if not event.is_reply:
        await event.reply("يرجى الرد على رسالة المستخدم الذي تريد رفعه.")
        return

    reply = await event.get_reply_message()
    sender_id = event.sender_id

    # بداية الجلسة
    admin_sessions[sender_id] = {
        "target_id": reply.sender_id,
        "rights": ChatAdminRights()
    }

    # توليد الأزرار
    buttons = [
        [Button.inline(f"{rights_map.get(b, ('', b))[1]}", b.encode()) for b in row]
        for row in buttons_layout
    ]

    await event.reply("اختر الصلاحيات التي تريد منحها للمستخدم:", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = event.sender_id
    session = admin_sessions.get(sender)

    if not session:
        await event.answer("انتهت الجلسة أو غير مصرح لك.", alert=True)
        return

    data = event.data.decode("utf-8")
    chat = event.chat_id

    if data == "cancel":
        admin_sessions.pop(sender, None)
        await event.edit("❌ تم إلغاء العملية.")
        return

    if data == "promote":
        session = admin_sessions.pop(sender)
        rights = session['rights']
        target_id = session['target_id']

        try:
            await bot(EditAdminRequest(
                channel=chat,
                user_id=target_id,
                admin_rights=rights,
                rank="مشرف"
            ))

            granted_rights = []
            for code, (attr, desc) in rights_map.items():
                if getattr(rights, attr, False):
                    granted_rights.append(f"• {desc}")

            desc = "\n".join(granted_rights) if granted_rights else "بدون صلاحيات"

            await event.edit(
                f"✅ تم رفع المستخدم مشرفًا بالصلاحيات التالية:\n{desc}",
                buttons=[Button.inline("✏️ تغيير اللقب", f"change_nick:{target_id}".encode())]
            )

        except Exception as e:
            await event.edit(f"❌ حدث خطأ أثناء تنفيذ الأمر:\n{e}")
        return

    # تفعيل صلاحية معينة
    if data in rights_map:
        attr, desc = rights_map[data]
        session["rights"].__setattr__(attr, True)

        # حالة خاصة للـ stories تتضمن ثلاث صلاحيات
        if data == "stories":
            session["rights"].post_stories = True
            session["rights"].edit_stories = True
            session["rights"].delete_stories = True

        await event.answer(f"✔️ تم تفعيل: {desc}")

@bot.on(events.CallbackQuery(pattern=b"change_nick:(\\d+)"))
async def change_nickname(event):
    target_id = int(event.pattern_match.group(1))
    sender = event.sender_id
    admin_sessions[sender] = {"target_id": target_id}
    await event.respond("✏️ أرسل اللقب الجديد في رسالة الآن.")

bot.run_until_disconnected()
