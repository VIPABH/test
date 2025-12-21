from ABH import ABH
from Resources import hint
from telethon import events

MAX_LINES_PER_MESSAGE = 500

@ABH.on(events.NewMessage(pattern='list'))
async def get_group_member_ids(e):
    await hint("sending...")

    buffer = []
    count = 0

    async for user in ABH.iter_participants(-1001882405904):
        buffer.append(str(user.id))
        count += 1

        if count >= MAX_LINES_PER_MESSAGE:
            await hint("\n".join(buffer))
            print(buffer)
            buffer.clear()
            count = 0

    if buffer:
        await hint("\n".join(buffer))
    await hint("Done!")
