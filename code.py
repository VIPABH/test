from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import events
from ABH import ABH
import asyncio
import traceback

@ABH.on(events.Raw)
async def monitor_restriction(event):
    try:
        me = await ABH.get_me()

        # محاولة استخراج user_id و channel_id
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", None) or getattr(participant, "user_id", None)

        # fallback لو user_id غير موجود
        if user_id is None and hasattr(event, "chat_id"):
            user_id = me.id
            channel_id = event.chat_id

        # نتابع فقط إذا الحدث متعلق بالبوت
        if user_id != me.id or channel_id is None:
            return

        # الحصول على كيان القناة أو المجموعة
        try:
            entity = await ABH.get_entity(channel_id)
        except:
            return

        # التحقق من تقييد البوت
        try:
            perms = await ABH.get_permissions(entity, me.id)
            if getattr(perms, "banned_rights", None):
                # تم تقييد البوت، طباعة رسالة وترك القناة
                print("تم تقييد البوت! 👋")
                try:
                    await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
                except:
                    pass
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))
        except:
            return

    except Exception:
        traceback.print_exc()
