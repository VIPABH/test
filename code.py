from ABH import ABH
from Resources import hint
from telethon import events
from telethon.tl.types import ChannelParticipantsSearch

GROUP_ID = -1001882405904
MAX_LINES_PER_MESSAGE = 1000

buffer = []
@ABH.on(events.NewMessage(pattern='list'))
async def get_group_member_ids(e):

    await hint(str(buffer))
    count = 0

    async for user in ABH.iter_participants(e.chat_id):
        buffer.append(str(user.id))
        count += 1

        if count >= 1000:
            await hint("\n".join(buffer))
            buffer.clear()
            count = 0

    if buffer:
        await hint("\n".join(buffer))
