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
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import FloodWaitError, ChatAdminRequiredError, UserAdminInvalidError
import asyncio

@ABH.on(events.NewMessage(pattern=r'/unban(?: (\d+))?'))
async def unban_handler(event):
    user_id = None
    
    # 1. جلب ID المستخدم (من الرد أو الرقم المكتوب)
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
    elif event.pattern_match.group(1):
        user_id = int(event.pattern_match.group(1))
    
    if not user_id:
        return await event.respond("⚠️ ارسل الـ ID مع الأمر أو قم بالرد على رسالة الشخص.")

    # 2. إنشاء كائن الحقوق "الخام" (الكل False لإلغاء الحظر)
    # هذا يحل مشكلة الكلمات المحجوزة مثل embed_links
    unban_rights = ChatBannedRights(
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

    try:
        # محاولة فك الحظر باستخدام الطلب المباشر (الأكثر توافقاً)
        await ABH(EditBannedRequest(event.chat_id, user_id, unban_rights))
        await event.respond(f"✅ تم فك الحظر عن: `{user_id}`")

    except Exception as e:
        # 3. خطة الطوارئ للمجموعات العادية (ValueError: You must pass either a channel...)
        try:
            # استخدام الدالة المختصرة بدون معاملات نصية لتجنب أخطاء الإصدارات
            await ABH.edit_permissions(event.chat_id, user_id, view_messages=True)
            await event.respond(f"✅ تم فك القيود عن: `{user_id}`")
        except Exception as final_e:
            await event.respond(f"❌ تعذر فك الحظر: {str(final_e)}")

    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await unban_handler(event)
@ABH.on(events.NewMessage(pattern=r'/del (.+)'))
async def delete_handler(event):
    # كود الحذف الخاص بك هنا
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

