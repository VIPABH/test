from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import events
from telethon.tl import types
from ABH import ABH
import asyncio
import traceback

@ABH.on(events.ChatAction)
async def monitor_bot_events(event):
    try:
        me = await ABH.get_me()
        print(f"[DEBUG] Logged in as: {me.id} ({me.first_name})")

        # نراقب فقط الأحداث التي تؤثر على البوت نفسه
        affected_ids = [user.id for user in getattr(event, "users", [])] if hasattr(event, "users") else []
        if me.id not in affected_ids:
            return  # الحدث لا يخص البوت

        channel_id = event.chat_id
        print(f"[DEBUG] Event affects bot in chat: {channel_id}")

        # الحصول على كيان المجموعة أو القناة
        try:
            entity = await ABH.get_entity(channel_id)
            print(f"[DEBUG] entity id: {entity.id}")
        except Exception as err:
            print(f"[DEBUG] Failed to get entity: {err}")
            return

        # التحقق من التقييد بدقة أكبر
        try:
            perms = await ABH.get_permissions(entity, me.id)
            print(f"[DEBUG] Bot permissions: {perms}")

            banned = getattr(perms, "banned_rights", None)
            if banned:
                # تحقق من أي تقييد يخص إرسال الرسائل أو الوسائط أو الملصقات
                restricted = (
                    getattr(banned, "send_messages", True) is False or
                    getattr(banned, "send_media", True) is False or
                    getattr(banned, "send_stickers", True) is False
                )
                if restricted:
                    print("[DEBUG] Bot is restricted in sending content!")
                    try:
                        await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
                    except Exception as e:
                        print(f"[DEBUG] Couldn't send message (maybe muted): {e}")
                    await asyncio.sleep(1)
                    await ABH(LeaveChannelRequest(channel_id))
                    return

        except Exception as err:
            print(f"[DEBUG] Failed to get permissions: {err}")

        # إرسال رسالة شكر إذا كان البوت أدمن
        try:
            if getattr(perms, "is_admin", False):
                print("[DEBUG] Bot is admin, sending thank-you message.")
                try:
                    message = await ABH.get_messages("recoursec", ids=22)
                    if message and getattr(message, "media", None):
                        x = await ABH.send_file(entity, message.media)
                        await ABH.send_message(entity, f"اشكرك على الاضافة ( {me.first_name} )", reply_to=x.id)
                    else:
                        await ABH.send_message(entity, f"اشكرك على الاضافة ( {me.first_name} )")
                except Exception as e:
                    print(f"[DEBUG] Failed to send thank-you message: {e}")
            else:
                # إذا لم يكن أدمن، يغادر المجموعة
                print("[DEBUG] Bot is not admin, leaving group.")
                try:
                    await ABH.send_message(entity, "😢")
                except:
                    pass
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))

        except Exception as e:
            print(f"[DEBUG] Error during response handling: {e}")

    except Exception:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
        return
