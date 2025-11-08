from telethon import events
from telethon.tl.types import UpdateChannelParticipant
from telethon.tl.functions.channels import LeaveChannelRequest
from Resources import *
from ABH import ABH

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        print("📦 نوع التحديث:", type(event))

        # نتحقق أن التحديث من نوع انضمام أو تغيير مشارك
        if isinstance(event, UpdateChannelParticipant):
            me = await ABH.get_me()

            # استخراج معرف القناة والمستخدم بطريقة آمنة
            channel_id = getattr(event, "channel_id", None)
            user_id = getattr(event, "user_id", None)

            # بعض الأنواع الفرعية من UpdateChannelParticipant تحتوي participant داخلي
            if not user_id and hasattr(event, "participant"):
                user_id = getattr(event.participant, "user_id", None)

            # فقط إذا الحدث يخص البوت نفسه
            if user_id == me.id and channel_id:
                try:
                    # نحاول جلب صلاحيات البوت داخل القناة
                    perms = await ABH.get_permissions(channel_id, me.id)
                    entity = await ABH.get_entity(channel_id)

                    if perms.is_admin:
                        await ABH.send_message(
                            entity,
                            f"✅ اشكرك على الاضافه {await mention(event)}"
                        )
                    else:
                        await ABH.send_message(
                            entity,
                            "⚠️ عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا."
                        )
                        await ABH(LeaveChannelRequest(channel_id))
                except Exception as e:
                    print(f"⚠️ خطأ أثناء التحقق من الصلاحيات: {e}")

        # else:
        #     print("🧩 نوع تحديث آخر غير متعلق بالمشاركين.")

    except Exception as e:
        print(f"🚨 حدث خطأ أثناء معالجة التحديث: {e}")
