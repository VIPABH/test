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

        # استخراج channel_id و user_id
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

        print(f"[STEP] الحدث متعلق بالبوت")
        print(f"[STEP] channel_id: {channel_id}, user_id: {user_id}")

        # الحصول على كيان القناة أو المجموعة
        try:
            entity = await ABH.get_entity(channel_id)
            print(f"[STEP] تم الحصول على الكيان: {entity.id}")
        except Exception as err:
            print(f"[ERROR] فشل الحصول على الكيان: {err}")
            return

        # التحقق من صلاحيات البوت
        try:
            perms = await ABH.get_permissions(entity, me.id)
            print(f"[STEP] صلاحيات البوت تم الحصول عليها")
            
            if getattr(perms, "banned_rights", None):
                print("[ALERT] تم تقييد البوت! 👋")
                try:
                    await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
                except:
                    print("[WARN] فشل إرسال رسالة التقييد")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))
                print("[STEP] البوت غادر القناة بعد التقييد")
        except Exception as err:
            print(f"[ERROR] فشل الحصول على الصلاحيات: {err}")

    except Exception:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
