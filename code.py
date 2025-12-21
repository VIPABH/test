from ABH import ABH
from Resources import hint
from telethon import events
from telethon.errors import FloodWaitError
import asyncio
@ABH.on(events.NewMessage(pattern='list'))
async def ban_all(e):
    banned = 0
    async for user in ABH.iter_participants(-1002219196756):
        try:
            await ABH.ban_user(-1002219196756, user.id)
            await asyncio.sleep(0.5)
            banned += 1
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
            try:
                await ABH.ban_user(-1002219196756, user.id)
                banned += 1
            except Exception:
                continue
        except Exception:
            continue
    await hint(f"Done! Total banned: {banned}")
