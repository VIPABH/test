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
from telethon import events
from telethon.tl.types import ChatBannedRights

@ABH.on(events.NewMessage(pattern=r'unban (\d+)'))
async def unban_user(e):
    user_id = int(e.pattern_match.group(1))

    # رفع الحظر جزئي: يسمح بالمراسلة النصية فقط، لكن يمنع إرسال الملفات والوسائط
    rights = ChatBannedRights(
        until_date=0,  # 0 = رفع الحظر نهائيًا
        view_messages=False,          # يستطيع رؤية الرسائل
        send_messages=False,          # إذا تريد السماح بالنص، اجعله False
        send_media=True,              # True = ممنوع إرسال أي وسائط
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
        send_polls=True,
        change_info=False,
        invite_users=False,
        pin_messages=False,
        manage_topics=False,
        send_photos=True,
        send_videos=True,
        send_roundvideos=True,
        send_audios=True,
        send_voices=True,
        send_docs=True,
        send_plain=False               # يسمح بإرسال النصوص
    )

    try:
        await ABH.edit_permissions(GROUP_ID, user_id, rights)
        await e.respond(f"✅ User {user_id} has been partially unbanned (cannot send files/media).")
    except Exception as exc:
        await e.respond(f"❌ Failed to update permissions for user {user_id}: {exc}")
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
