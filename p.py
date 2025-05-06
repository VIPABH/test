from telethon import TelegramClient, events, Button
import os
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    global tid
    tid = event.sender_id
    await event.reply(
        "ارسل الصلاحيات",
        buttons=[
            Button.inline("تعديل معلومات المجموعة", b"edit"),
            Button.inline("حظر المستخدمين", b"ban"),
            Button.inline("حذف الرسائل", b"delete"),
            Button.inline("تثبيت الرسائل", b"pin"),
            Button.inline("إضافة مستخدمين", b"invite"),
            Button.inline("إدارة الدعوات", b"invite_link"),
            Button.inline("إدارة الرسائل", b"messages"),
        ]
    )
@bot.on(events.CallbackQuery(data=b"edit"))
async def edit_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        change_info=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات تعديل معلومات المجموعة")
@bot.on(events.CallbackQuery(data=b"ban"))
async def ban_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        ban_users=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات حظر المستخدمين")
@bot.on(events.CallbackQuery(data=b"delete"))
async def delete_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        delete_messages=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات حذف الرسائل")
@bot.on(events.CallbackQuery(data=b"pin"))
async def pin_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        pin_messages=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات تثبيت الرسائل")
@bot.on(events.CallbackQuery(data=b"invite"))
async def invite_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        invite_users=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات إضافة مستخدمين")
@bot.on(events.CallbackQuery(data=b"invite_link"))
async def invite_link_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        manage_invite_links=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات إدارة الدعوات")
@bot.on(events.CallbackQuery(data=b"messages"))
async def messages_permissions(event):
    chat = event.chat_id
    rights = ChatAdminRights(
        manage_chat=True)
    await bot(EditAdminRequest(chat, tid, rights, rank="︎ ︎ ︎ ︎ ︎ ︎ ︎ ︎"))
    await event.answer("تمت إضافة صلاحيات إدارة الرسائل")
@bot.on(events.CallbackQuery(data=b"cancel"))
async def cancel_permissions(event):
    await event.answer("تم إلغاء العملية")
    await event.delete()
@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change_nickname(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        if reply_message:
            new_nickname = reply_message.text
            chat = event.chat_id
            rights = ChatAdminRights(
                change_info=True)
            await bot(EditAdminRequest(chat, tid, rights, rank=new_nickname))
            await event.reply("تم تغيير اللقب بنجاح")
        else:
            await event.reply("يرجى الرد على رسالة تحتوي على اللقب الجديد.")
    else:
        await event.reply("يرجى الرد على رسالة تحتوي على اللقب الجديد.")
bot.run_until_disconnected()
