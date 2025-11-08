from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from Resources import *
from ABH import ABH

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        update = getattr(event, "update", event)
        print("📦 نوع التحديث:", type(update))

        # تحقق أن التحديث يخص القنوات
        if isinstance(update, UpdateChannelParticipant):
            me = await ABH.get_me()

            # نحاول الحصول على user_id بشكل آمن
            user_id = getattr(update, "user_id", None)
            if not user_id and hasattr(update, "participant"):
                user_id = getattr(update.participant, "user_id", None)

            channel_id = getattr(update, "channel_id", None)

            # فقط إذا كان الحدث يخص البوت نفسه
            if user_id == me.id and channel_id:
                try:
                    perms = await ABH.get_permissions(channel_id, me.id)
                    entity = await ABH.get_entity(channel_id)

                    if perms.is_admin:
                        await ABH.send_message(
                            entity,
                            f"✅ اشكرك على الاضافة {await mention(update)}"
                        )
                    else:
                        await ABH.send_message(
                            entity,
                            "⚠️ عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا."
                        )
                        await ABH(LeaveChannelRequest(channel_id))
                except Exception as e:
                    print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")

    except Exception as e:
        print(f"🚨 حدث خطأ أثناء معالجة التحديث: {e}")
