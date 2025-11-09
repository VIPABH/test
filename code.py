from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import events, Button, types
from ABH import ABH
import asyncio
import traceback

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        me = await ABH.get_me()
        print(f"[DEBUG] Logged in as: {me.id} ({me.first_name})")

        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", getattr(participant, "user_id", None))

        print(f"[DEBUG] channel_id: {channel_id}")
        print(f"[DEBUG] participant: {type(participant).__name__ if participant else None}")
        print(f"[DEBUG] user_id: {user_id}")

        if user_id != me.id or channel_id is None or participant is None:
            print("[DEBUG] Skipped: not related to me or missing data.")
            return

        # تحقق من التقييد
        if isinstance(participant, types.ChannelParticipantRestricted):
            print("[DEBUG] Bot is restricted!")
            try:
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
            except Exception as err:
                print(f"[DEBUG] Couldn't send message (probably muted): {err}")
            await asyncio.sleep(1)
            print("[DEBUG] Leaving channel due to restriction.")
            await ABH(LeaveChannelRequest(channel_id))
            return

        # معالجة التحديث والفاعل
        update = getattr(event, "update", event)
        actor_id = getattr(update, "actor_id", None) or getattr(update, "user_id", None)
        print(f"[DEBUG] actor_id: {actor_id}")

        mention = "شخص مجهول"
        if actor_id:
            try:
                actor = await ABH.get_entity(actor_id)
                mention = f"[{getattr(actor, 'first_name', 'مستخدم')}](tg://user?id={actor.id})"
                print(f"[DEBUG] actor: {actor.id} ({actor.first_name})")
            except Exception as err:
                print(f"[DEBUG] Failed to get actor entity: {err}")

        # الحصول على كيان المجموعة
        try:
            entity = await ABH.get_entity(channel_id)
            print(f"[DEBUG] entity: {entity.id}")
        except Exception as err:
            print(f"[DEBUG] Failed to get entity: {err}")
            return

        # فحص صلاحيات البوت
        try:
            perms = await ABH.get_permissions(entity, me.id)
            print(f"[DEBUG] is_admin: {perms.is_admin}")
        except Exception as err:
            print(f"[DEBUG] Failed to get permissions: {err}")
            perms = types.ChatAdminRights()

        # الحصول على الرسالة المرجعية
        try:
            message = await ABH.get_messages("recoursec", ids=22)
            print(f"[DEBUG] message found: {bool(message)}")
        except Exception as err:
            print(f"[DEBUG] Failed to get message: {err}")
            message = None

        # محاولة الحصول على عدد الأعضاء
        count = None
        try:
            chat = await event.get_input_chat()
            try:
                full_chat = await ABH(GetFullChatRequest(chat.chat_id))
                count = full_chat.full_chat.participants_count
                print(f"[DEBUG] participants_count: {count}")
            except Exception:
                full_ch = await ABH(GetFullChannelRequest(channel=channel_id))
                count = full_ch.full_chat.participants_count
                print(f"[DEBUG] participants_count (channel): {count}")
        except Exception as err:
            print(f"[DEBUG] Failed to get participants count: {err}")
            count = None

        # منطق الرد والإجراء
        if getattr(perms, "is_admin", False):
            print("[DEBUG] Bot is admin, sending thank-you message.")
            if message and getattr(message, "media", None):
                x = await ABH.send_file(entity, message.media)
                await ABH.send_message(entity, f"اشكرك على الاضافة وردة ( {mention} ) ", reply_to=x.id)
            else:
                await ABH.send_message(entity, f"اشكرك على الاضافة ( {mention} )")
        else:
            print("[DEBUG] Bot is not admin, leaving group.")
            await ABH.send_message(entity, "😢")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

    except Exception:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
        return
