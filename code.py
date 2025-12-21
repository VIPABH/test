from ABH import ABH
from Resources import hint
from telethon import events
@ABH.on(events.NewMessage(pattern='list'))
async def get_group_member_ids(e):
    buffer = []
    async for user in ABH.iter_participants(-1002219196756):
        if user.id in buffer:
            continue
        try:
            await ABH.ban_user(-1001882405904, user.id)
            buffer.append(int(user.id))
        except:
            continue
    await hint(f"Done! Total users: {len(buffer)}")
