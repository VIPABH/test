from ABH import ABH
from Resources import hint
from telethon import events, errors
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import asyncio
GROUP_ID = -1001882405904
ban_rights = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)
msg = None
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import FloodWaitError, UserNotParticipantError
import asyncio

# إعدادات الاتصال
# افترض أن ABH هو العميل:
# ABH = TelegramClient(...).start(...)

GROUP_ID = -1001234567890  # ضع هنا معرف المجموعة أو القناة

@ABH.on(events.NewMessage(pattern=r'/unban (.+)'))
async def unban_handler(event):
    target = event.pattern_match.group(1)

    try:
        # تحويل الـ username إلى participant
        if target.startswith('@'):
            participant = await ABH.get_entity(target)
        else:
            participant = int(target)

        # إعداد الصلاحيات لإلغاء الحظر
        rights = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_links=False
        )

        await ABH(EditBannedRequest(
            channel=GROUP_ID,
            participant=participant,
            banned_rights=rights
        ))

        await event.respond(f"✅ تم إلغاء الحظر عن المستخدم `{participant}` بنجاح!")

    except FloodWaitError as e:
        await event.respond(f"⏳ يجب الانتظار {e.seconds} ثانية بسبب FloodWait.")
        await asyncio.sleep(e.seconds)
        await unban_handler(event)
    except UserNotParticipantError:
        await event.respond("❌ المستخدم غير موجود في المجموعة أو غير محظور.")
    except ValueError:
        await event.respond("❌ يجب إدخال معرف رقمي صالح أو @username.")
    except Exception as e:
        await event.respond(f"❌ حدث خطأ: {e}")

@ABH.on(events.NewMessage(pattern='del (.+)'))
async def delete_message(e):
    message_ids = int(e.pattern_match.group(1))
    await ABH.delete_messages(GROUP_ID, message_ids)
    await hint(f"✅ Deleted messages with IDs: {message_ids}")
@ABH.on(events.NewMessage(pattern='fcb36'))
async def ban_all_debug(e):
    banned = 0
    skipped = 0
    entity = await ABH.get_entity(GROUP_ID)
    async for user in ABH.iter_participants(entity):
        try:
            if user.bot or user.is_self:
                skipped += 1
                continue
            await ABH(EditBannedRequest(
                channel=entity,
                participant=user.id,
                banned_rights=ban_rights
            ))
            banned += 1
            if msg:
                await ABH.send_message(GROUP_ID, f"{msg} {user.id}")
            await asyncio.sleep(0.5)
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
@ABH.on(events.NewMessage(pattern='msg (.+)'))
async def set_ban_msg(e):
    global msg
    msg = e.pattern_match.group(1)
    await hint(f"✅ Ban message set to: {msg}")
