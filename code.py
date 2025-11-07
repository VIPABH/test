from telethon import TelegramClient, events
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot

@bot.on(events.ChatAction)
async def check_admin(event):
    me = await bot.get_me()

    # تحقق عند إضافة البوت
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

    # تحقق عند تغيير الصلاحيات (رفع/تنزيل مشرف)
    elif getattr(event, "new_admin_rights", None) or getattr(event, "banned_rights", None):
        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            if not perms.is_admin:
                await event.reply("تم تنزيل البوت من الاشراف، سأخرج ❌")
                await bot(LeaveChannelRequest(event.chat_id))
        except Exception as e:
            print(f"خطأ عند التحقق من الصلاحيات بعد التغيير: {e}")
