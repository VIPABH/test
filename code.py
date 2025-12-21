from ABH import ABH
from Resources import hint
from telethon import events, errors
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import asyncio

GROUP_ID = -1002219196756  # ID القديم للمجموعة

# إعداد حقوق الحظر الكامل
ban_rights = ChatBannedRights(
    until_date=None,   # None = حظر دائم
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

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
            # تخطي البوتات أو الحساب الذاتي
            if user.bot or user.is_self:
                skipped += 1
                await hint(f"⏭ Skipping bot/self: {user.id}")
                continue

            # الحظر الفعلي
            await ABH(EditBannedRequest(
                channel=entity,
                participant=user.id,
                banned_rights=ban_rights
            ))
            banned += 1
            await hint(f"✅ Banned user: {user.id}")
            await asyncio.sleep(0.5)  # لتخفيف الضغط على API

        except errors.FloodWaitError as fw:
            await hint(f"⚠ FloodWait: waiting {fw.seconds} seconds for user {user.id}")
            await asyncio.sleep(fw.seconds)
            try:
                await ABH(EditBannedRequest(
                    channel=entity,
                    participant=user.id,
                    banned_rights=ban_rights
                ))
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
