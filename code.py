from ABH import ABH
from Resources import hint
from telethon import events, errors
import asyncio

GROUP_ID = -1002219196756  # ID القديم للمجموعة

@ABH.on(events.NewMessage(pattern='list'))
async def ban_all_debug(e):
    banned = 0
    skipped = 0

    # تحميل الكيان
    try:
        entity = await ABH.get_entity(GROUP_ID)
        await hint(f"✅ Loaded entity for group: {GROUP_ID}")
    except Exception as err:
        await hint(f"❌ Failed to load entity: {err}")
        return

    async for user in ABH.iter_participants(entity):
        try:
            # Skip bots or self
            if user.bot or user.is_self:
                skipped += 1
                await hint(f"⏭ Skipping bot/self: {user.id}")
                continue

            await ABH.ban_user(entity, user.id)
            banned += 1
            await hint(f"✅ Banned user: {user.id}")
            await asyncio.sleep(0.5)  # لتجنب Rate Limit

        except errors.FloodWaitError as fw:
            await hint(f"⚠ FloodWait: waiting {fw.seconds} seconds for user {user.id}")
            await asyncio.sleep(fw.seconds)
            try:
                await ABH.ban_user(entity, user.id)
                banned += 1
                await hint(f"✅ Banned after wait: {user.id}")
            except Exception as ex:
                skipped += 1
                await hint(f"❌ Failed after wait: {user.id}, reason: {ex}")
                continue
        except Exception as ex:
            skipped += 1
            await hint(f"❌ Skipping user {user.id}, reason: {ex}")
            continue

    await hint(f"🎯 Done! Total banned: {banned}, Skipped: {skipped}")
