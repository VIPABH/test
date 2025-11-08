from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from Resources import *
from ABH import ABH
@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        print("📦 نوع التحديث:", type(event))
        if isinstance(event, UpdateChannelParticipant):
            me = await ABH.get_me()
            msg = event.update.message
            if event.user_id == me.id:
                try:
                    perms = await ABH.get_permissions(event.channel_id, me.id)
                    if perms.is_admin:
                        await msg.reply(f"اشكرك على الاضافه {await mention(event)}")
                    else:
                        await msg.reply(f'عذرا بس ماكدر ابقه هنا الا ترفعني مشرف')
                        await ABH(LeaveChannelRequest(event.channel_id))
                except Exception as e:
                    print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")
        # else:
        #     print("🧩 نوع تحديث آخر غير متعلق بالمشاركين.")
        #     print(event)
    except Exception as e:
        print(f"🚨 حدث خطأ أثناء معالجة التحديث: {e}")
