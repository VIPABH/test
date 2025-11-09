from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import events
from ABH import ABH
import asyncio
import traceback

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        me = await ABH.get_me()
        print(f"[DEBUG] Logged in as: {me.id} ({me.first_name})")

        # محاولة استخراج user_id و channel_id بأكثر من طريقة
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", None) or getattr(participant, "user_id", None)

        print(f"[DEBUG] channel_id: {channel_id}")
        print(f"[DEBUG] participant: {type(participant).__name__ if participant else None}")
        print(f"[DEBUG] user_id: {user_id}")

        # fallback: لو user_id غير موجود، نفحص إذا الحدث مرتبط بالبوت بطريقة أخرى
        if user_id is None and hasattr(event, "chat_id"):
            user_id = me.id
            channel_id = event.chat_id
            print(f"[DEBUG] Fallback: using chat_id as channel_id and bot's id as user_id")

        # تجاهل الأحداث غير المتعلقة بالبوت أو بدون channel_id
        if user_id != me.id or channel_id is None:
            print("[DEBUG] Skipped: not related to me or missing data.")
            return

        # الحصول على كيان القناة أو المجموعة
        try:
            entity = await ABH.get_entity(channel_id)
            print(f"[DEBUG] entity: {entity.id}")
        except Exception as err:
            print(f"[DEBUG] Failed to get entity: {err}")
            return

        # التحقق من تقييد البوت
        try:
            perms = await ABH.get_permissions(entity, me.id)
            print(f"[DEBUG] permissions: {perms}")
            if getattr(perms, "banned_rights", None):
                print("[DEBUG] Bot is restricted!")
                try:
                    await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
                except:
                    print("[DEBUG] Failed to send restriction message")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))
                return
        except Exception as err:
            print(f"[DEBUG] Failed to get permissions: {err}")

    except Exception:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
