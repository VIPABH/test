from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot
import asyncio
@bot.on(events.Raw)
async def monitor_everything(event):
    try:
        print("📦 نوع التحديث:", type(event))
        if isinstance(event, UpdateChannelParticipant):
            print("⚙️ حدث يخص المشاركين أو المشرفين.")
            me = await bot.get_me()
            if event.user_id == me.id:
                print("👀 التغيير يخص البوت نفسه.")
                try:
                    perms = await bot.get_permissions(event.channel_id, me.id)
                    if perms.is_admin:
                        print("✅ البوت لا يزال مشرف.")
                    else:
                        print("❌ تم تنزيل البوت من الإشراف! يغادر الآن...")
                        await bot(LeaveChannelRequest(event.channel_id))
                except Exception as e:
                    print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")
        else:
            print("🧩 نوع تحديث آخر غير متعلق بالمشاركين.")
            print(event)
    except Exception as e:
        print(f"🚨 حدث خطأ أثناء معالجة التحديث: {e}")
