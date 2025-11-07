from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot

@bot.on(events.Raw)
async def monitor_admin_changes(event):
    if isinstance(event, UpdateChannelParticipant):
        me = await bot.get_me()
        if event.user_id == me.id:
            try:
                perms = await bot.get_permissions(event.channel_id, me.id)
                if not perms.is_admin:
                    print("❌ تم تنزيل البوت من الإشراف! يغادر الآن...")
                    await bot(LeaveChannelRequest(event.channel_id))
                else:
                    print("✅ البوت ما زال مشرف.")
            except Exception as e:
                print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")
