from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import ChatAdminRights
from telethon import TelegramClient, events
from ABH import ABH as bot
@bot.on(events.ChatAction)
async def check_admin(event):
    me = await bot.get_me()
    if event.user_added and event.user_id == me.id:
        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            if perms.is_admin:
                await event.reply("تم التأكد: البوت مشرف ✅")
            else:
                await event.reply("البوت ليس مشرف! سأخرج ❌")
                await bot(LeaveChannelRequest(event.chat_id))
        except Exception as e:
            print(f"خطأ عند التحقق من الصلاحيات: {e}")
