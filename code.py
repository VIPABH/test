from ABH import ABH
from Resources import hint
from telethon import events
@ABH.on(events.NewMessage(pattern='list'))
@ABH.on(events.NewMessage(pattern='list'))
async def get_group_member_ids(e):
    await hint("sending...")
    buffer = []
    c = 0
    async for user in ABH.iter_participants(-1001882405904):
        if user.id in buffer:
            continue
        buffer.append(int(user.id))
        c += 1
    await hint(f"Done! Total users: {c}")
