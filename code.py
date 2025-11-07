from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot

@bot.on(events.ChatAction)
async def monitor_admin(event):
    me = await bot.get_me()

    # نتحقق فقط إذا هناك تغيير في صلاحيات المشرفين
    if getattr(event, "new_admin_rights", None):
        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            if perms.is_admin:
                # البوت أصبح مشرف
                try:
                    await event.reply("تم رفع البوت إلى مشرف ✅")
                except:
                    pass  # إذا لا يملك صلاحية الكتابة
            else:
                # البوت تم تنزيله من المشرفين
                try:
                    await event.reply("تم تنزيل البوت من الاشراف! سأخرج ❌")
                except:
                    pass
                try:
                    await bot(LeaveChannelRequest(event.chat_id))
                except:
                    pass
        except:
            # في حالة فشل الحصول على الصلاحيات، نخرج على أي حال
            try:
                await bot(LeaveChannelRequest(event.chat_id))
            except:
                pass
