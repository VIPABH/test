from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot

@bot.on(events.ChatAction)
async def check_admin(event):
    me = await bot.get_me()

    # الحدث يخص البوت نفسه
    if event.user_added and event.user_id == me.id:
        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            if perms.is_admin:
                await event.reply("تم التأكد: البوت مشرف ✅")
            else:
                await event.reply("البوت ليس مشرف! سأخرج ❌")
                await bot(LeaveChannelRequest(event.chat_id))
        except:
            # إذا حدث أي خطأ في جلب الصلاحيات أو الخروج
            try:
                await bot(LeaveChannelRequest(event.chat_id))
            except:
                pass

    # تحقق عند أي تغيير صلاحيات
    elif getattr(event, "new_admin_rights", None):
        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            if not perms.is_admin:
                await event.reply("تم تنزيل البوت من الاشراف! سأخرج ❌")
                await bot(LeaveChannelRequest(event.chat_id))
        except:
            try:
                await bot(LeaveChannelRequest(event.chat_id))
            except:
                pass
