from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage(pattern="/المالك"))
async def get_owner(event):
    if not event.is_group:
        return await event.reply("❌ هذا الأمر يعمل فقط في المجموعات.")
    
    chat = await event.get_chat()

    if getattr(chat, 'megagroup', False):
        # ✅ مجموعة من نوع SuperGroup
        try:
            result = await ABH(GetParticipantsRequest(
                channel=chat,
                filter=ChannelParticipantsAdmins(),
                offset=0,
                limit=100,
                hash=0
            ))

            for participant in result.participants:
                if isinstance(participant, ChannelParticipantCreator):
                    user = await ABH.get_entity(participant.user_id)
                    return await event.reply(
                        f"👑 مالك السوبرگروب هو: [{user.first_name}](tg://user?id={user.id})"
                    )
            return await event.reply("❌ لم أتمكن من تحديد المالك.")
        except Exception as e:
            return await event.reply(f"🚫 حدث خطأ أثناء محاولة معرفة المالك: {e}")

    else:
        # ✅ مجموعة عادية (Group)
        # يمكن فقط جلب من أنشأ المجموعة عبر event.message.chat.creator (إن توفر)
        try:
            participants = await ABH.get_participants(chat.id)
            for user in participants:
                if user.bot:
                    continue
                if user.id == chat.creator_id:
                    return await event.reply(
                        f"👑 منشئ المجموعة هو: [{user.first_name}](tg://user?id={user.id})"
                    )
            return await event.reply("❌ لم أتمكن من تحديد منشئ المجموعة.")
        except:
            return await event.reply("❌ هذه مجموعة عادية ولا يمكن تحديد المالك بدقة.")
