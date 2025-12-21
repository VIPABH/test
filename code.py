from ABH import ABH
from Resources import hint
from telethon.tl.types import ChannelParticipantsSearch
MAX_LINES_PER_MESSAGE = 1000 
async def get_group_member_ids():
    await hint("sendeing")
    buffer = []
    line_count = 0
    async for user in ABH.iter_participants(
        -1001882405904,
        filter=ChannelParticipantsSearch('')
    ):
        buffer.append(str(user.id))
        line_count += 1
        if line_count >= MAX_LINES_PER_MESSAGE:
            await hint("\n".join(buffer))
            buffer.clear()
            line_count = 0
    if buffer:
        await hint("\n".join(buffer))
