from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage(pattern="/المالك"))
async def get_owner(event):
    if not event.is_group:
        return await event.reply("❌ هذا الأمر يعمل في المجموعات فقط.")
    
    chat = await event.get_chat()
    result = await ABH(GetParticipantsRequest(
        channel=chat.id,
        filter=ChannelParticipantsAdmins(),
        offset=0,
        limit=100,
        hash=0
    ))

    # ابحث عن المالك الحقيقي عبر النوع ChannelParticipantCreator
    for participant in result.participants:
        if isinstance(participant, ChannelParticipantCreator):
            user = await ABH.get_entity(participant.user_id)
            return await event.reply(
                f"👑 مالك المجموعة هو: [{user.first_name}](tg://user?id={user.id})"
            )

    await event.reply("لم أتمكن من تحديد مالك المجموعة.")
