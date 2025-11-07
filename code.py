from telethon import TelegramClient, events
from telethon.tl.types import ChatAdminRights
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
                await bot.kick_participant(event.chat_id, me.id)
        except Exception as e:
            print(f"خطأ عند التحقق من الصلاحيات: {e}")
