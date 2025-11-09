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
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", getattr(participant, "user_id", None))

        # لا نستمر إلا إذا التغيير يخص البوت، ومع وجود channel_id وparticipant
        if user_id != me.id or channel_id is None or participant is None:
            return

        # حالة التقييد
        if isinstance(participant, types.ChannelParticipantRestricted):
            try:
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
            except Exception:
                # لو التقييد يمنع إرسال الرسائل فنتجاوز
                pass
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
            return

        # نحاول استخراج الـ update والـ actor بالشكل الأكثر مرونة
        update = getattr(event, "update", event)
        actor_id = getattr(update, "actor_id", None) or getattr(update, "user_id", None)
        mention = "شخص مجهول"

        if actor_id:
            try:
                actor = await ABH.get_entity(actor_id)
                mention = f"[{getattr(actor, 'first_name', 'مستخدم')}](tg://user?id={actor.id})"
            except Exception:
                # لو فشل الحصول على المعرّف، نكمل بدون mention مفصّل
                pass

        # نأخذ الكيان ونتأكد من صلاحيات البوت على شكل صحيح
        try:
            entity = await ABH.get_entity(channel_id)
        except Exception:
            # لا نستطيع الوصول للكيان -> نخرج
            return

        # استخدم entity عند طلب الصلاحيات (أكثر موثوقية)
        try:
            perms = await ABH.get_permissions(entity, me.id)
        except Exception:
            perms = types.ChatAdminRights()  # fallback بسيط إن فشل الاستدعاء

        # الحصول على الرسالة المرجعية (حماية من الفشل)
        try:
            message = await ABH.get_messages("recoursec", ids=22)
        except Exception:
            message = None

        # محاولة آمنة للحصول على عدد المشاركين (تجربة GetFullChat ثم GetFullChannel)
        count = None
        try:
            chat = await event.get_input_chat()
            try:
                full_chat = await ABH(GetFullChatRequest(chat.chat_id))
                count = full_chat.full_chat.participants_count
            except Exception:
                # إن فشل، نجرب كقناة
                try:
                    full_ch = await ABH(GetFullChannelRequest(channel=channel_id))
                    count = full_ch.full_chat.participants_count
                except Exception:
                    count = None
        except Exception:
            count = None

        # منطقك السابق المعتمد على صلاحيات الادمن
        if getattr(perms, "is_admin", False):
            if message and getattr(message, "media", None):
                x = await ABH.send_file(entity, message.media)
                await ABH.send_message(entity, f"اشكرك على الاضافة وردة ( {mention} ) ", reply_to=x.id)
            else:
                await ABH.send_message(entity, f"اشكرك على الاضافة ( {mention} )")
        else:
            await ABH.send_message(entity, "😢")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

    except Exception:
        # طباعة التتبع الكامل للاخطأ بحيث يظهر عند التشغيل
        traceback.print_exc()
        return
