from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from Resources import *
from ABH import ABH

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        update = event.update  # ← هذا هو الكائن الحقيقي
        print("📦 نوع التحديث:", type(update))

        # تحقق من نوع التحديث الصحيح
        if isinstance(update, UpdateChannelParticipant):
            me = await ABH.get_me()

            user_id = getattr(update.participant, "user_id", None)
            channel_id = getattr(update, "channel_id", None)

            # نتأكد أن الحدث يخص البوت نفسه
            if user_id == me.id:
                try:
                    perms = await ABH.get_permissions(channel_id, me.id)
                    entity = await ABH.get_entity(channel_id)

                    if perms.is_admin:
                        await ABH.send_message(
                            entity,
                            f"اشكرك على الاضافة {await mention(update)}"
                        )
                    else:
                        await ABH.send_message(
                            entity,
                            "عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا."
                        )
                        await ABH(LeaveChannelRequest(channel_id))

                except Exception as e:
                    print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")
        else:
            # مجرد تتبع للتحديثات الأخرى
            pass

    except Exception as e:
        print(f"🚨 حدث خطأ أثناء معالجة التحديث: {e}")
