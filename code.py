import asyncio
from telethon import events
from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantCreator

# استيراد كيان البوت باسم ABH من ملف ABH
from ABH import ABH

@ABH.on(events.Raw(UpdateChannelParticipant))
async def on_owner_transfer(event):
    # الفحص المباشر: هل التحديث الصادر يحتوي على إسناد صلاحية المالك (Creator)؟
    if isinstance(event.new_participant, ChannelParticipantCreator):
        raw_chat_id = event.channel_id
        # ضبط تنسيق آيدي القناة بالشكل القياسي לתليجرام (-100xxxx)
        channel_id = int(f"-100{raw_chat_id}") if not str(raw_chat_id).startswith("-100") else raw_chat_id
        
        new_owner_id = event.new_participant.user_id
        actor_id = getattr(event, 'actor_id', 'غير محدد')

        msg = (
            f"⚠️ **تنبيه: تم نقل ملكية هذه القناة!**\n\n"
            f"👤 **المالك الجديد:** `{new_owner_id}`\n"
            f"🛠 **بواسطة:** `{actor_id}`"
        )

        # إرسال التنبيه الفوري لنفس القناة مباشرة
        await ABH.send_message(channel_id, msg)
