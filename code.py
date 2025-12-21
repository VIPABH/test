from ABH import ABH
from Resources import hint
from telethon import events, errors
import asyncio

GROUP_ID = -1002219196756  # ID القديم للمجموعة

@ABH.on(events.NewMessage(pattern='list'))
async def ban_all(e):
    banned = 0

    # التأكد من تحميل الكيان مسبقًا
    try:
        entity = await ABH.get_entity(GROUP_ID)
    except Exception as err:
        await hint(f"❌ فشل تحميل الكيان: {err}")
        return

    async for user in ABH.iter_participants(entity):
        try:
            await ABH.ban_user(entity, user.id)
            banned += 1
            await asyncio.sleep(0.5)  # لتجنب Rate Limit
        except errors.FloodWaitError as fw:
            await hint(f"FloodWait: waiting {fw.seconds} seconds")
            await asyncio.sleep(fw.seconds)
            try:
                await ABH.ban_user(entity, user.id)
                banned += 1
            except Exception:
                continue
        except Exception:
            continue

    await hint(f"Done! Total banned: {banned}")
