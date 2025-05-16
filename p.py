from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

admin_sessions = {1910015590, 1910015590}

@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    if not event.is_reply:
        await event.reply("يرجى الرد على رسالة المستخدم الذي تريد رفعه.")
        return

    reply = await event.get_reply_message()
    sender_id = event.sender_id
    admin_sessions[sender_id] = {
        "target_id": reply.sender_id,
        "rights": ChatAdminRights()
    }
    buttons=[
        [Button.inline("🛠️ manage_call", b"manage_call"),
        [Button.inline("🛠️ تعديل معلومات", b"edit"),
         Button.inline("🔨 حظر المستخدمين", b"ban")],
        [Button.inline("🗑️ حذف الرسائل", b"delete"),
         Button.inline("📌 تثبيت الرسائل", b"pin")],
        [Button.inline("➕ دعوة مستخدمين", b"invite"),
         Button.inline("🔗 إدارة الدعوات", b"invite_link")],
        [Button.inline("💬 إدارة الرسائل", b"messages"),
         Button.inline("📚 إدارة الستوري", b"stories")],
        [Button.inline("📞 صلاحيات الاتصال", b"calls"),
         Button.inline("👤 تعيين مشرفين", b"add_admins")],
        [Button.inline("✅ تنفيذ", b"promote"),
         Button.inline("❌ إلغاء", b"cancel")]
        ]]

    await event.reply(
        "اختر الصلاحيات التي تريد منحها للمستخدم:",
            Button=buttons
    )
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
            if rights.change_info:
                granted_rights.append("تعديل معلومات المجموعة")
            if rights.ban_users:
                granted_rights.append("حظر المستخدمين")
            if rights.delete_messages:
                granted_rights.append("حذف الرسائل")
            if rights.pin_messages:
                granted_rights.append("manage_call")
            if rights.manage_call:
                granted_rights.append("تثبيت الرسائل")
            if rights.invite_users:
                granted_rights.append("دعوة مستخدمين")
            if any([getattr(rights, "post_stories", False), getattr(rights, "edit_stories", False), getattr(rights, "delete_stories", False)]):
                granted_rights.append("إدارة الستوري")
            if getattr(rights, "manage_call", False):  # الاسم الصحيح
                granted_rights.append("صلاحيات الاتصال")
            if rights.add_admins:
                granted_rights.append("تعيين مشرفين")

            desc = "\n• " + "\n• ".join(granted_rights) if granted_rights else "بدون صلاحيات مذكورة"

            await event.edit(
                f"✅ تم رفع المستخدم مشرفًا بالصلاحيات التالية:\n{desc}",
                buttons=[Button.inline("✏️ تغيير اللقب", f"change_nick:{target_id}".encode())]
            )

        except Exception as e:
            await event.edit(f"❌ حدث خطأ أثناn{e}")
        return

    rights = session["rights"]

    if data == "edit":
        rights.manage_call = True
        await event.answer("✔️ تم تفعيل: manage_call")
    if data == "edit":
        rights.change_info = True
        await event.answer("✔️ تم تفعيل: تعديل معلومات المجموعة")
    elif data == "ban":
        rights.ban_users = True
        await event.answer("✔️ تم تفعيل: حظر المستخدمين")
    elif data == "delete":
        rights.delete_messages = True
        await event.answer("✔️ تم تفعيل: حذف الرسائل")
    elif data == "pin":
        rights.pin_messages = True
        await event.answer("✔️ تم تفعيل: تثبيت الرسائل")
    elif data == "invite":
        rights.invite_users = True
        await event.answer("✔️ تم تفعيل: دعوة مستخدمين")
    elif data == "invite_link":
        rights.manage_invite_links = True
        await event.answer("✔️ تم تفعيل: إدارة الدعوات")
    elif data == "messages":
        rights.manage_chat = True
        await event.answer("✔️ تم تفعيل: إدارة الرسائل")
    elif data == "stories":
        rights.post_stories = True
        rights.edit_stories = True
        rights.delete_stories = True
        await event.answer("✔️ تم تفعيل: إدارة الستوري")
    elif data == "calls":
        rights.manage_calls = True
        await event.answer("✔️ تم تفعيل: صلاحيات الاتصال")
    elif data == "add_admins":
        rights.add_admins = True
        await event.answer("✔️ تم تفعيل: تعيين مشرفين")

@bot.on(events.CallbackQuery(pattern=b"change_nick:(\\d+)"))
async def change_nickname(event):
    target_id = int(event.pattern_match.group(1))
    sender = event.sender_id

    admin_sessions[sender] = {"target_id": target_id}
    await event.respond("✏️ أرسل اللقب الجديد في رسالة عادية الآن.")


bot.run_until_disconnected()
