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
from telethon.errors import FloodWaitError, ChatAdminRequiredError
import asyncio

# ملاحظة: تأكد أن ABH معرف مسبقاً في ملفك الأساسي
# @ABH.on...

@ABH.on(events.NewMessage(pattern=r'/unban (\d+)'))
async def unban_handler(event):
    # الحصول على ID المستخدم من الرسالة
    user_id = int(event.pattern_match.group(1))
    # الحصول على ID المجموعة الحالية تلقائياً
    chat_id = event.chat_id 

    try:
        # الطريقة الأبسط والأضمن لإلغاء الحظر في Telethon
        # نضع كل الصلاحيات كـ False لإلغاء أي قيود (Unban/Unmute)
        await ABH.edit_permissions(
            chat_id, 
            user_id, 
            view_messages=True, # السماح له برؤية الرسائل (إلغاء الحظر الكلي)
            send_messages=True, 
            send_media=True, 
            send_stickers=True, 
            send_gifs=True, 
            send_games=True, 
            send_inline=True, 
            embed_links=True
        )
        
        await event.respond(f"✅ تم إلغاء الحظر عن المستخدم `{user_id}` في هذه المجموعة.")

    except FloodWaitError as e:
        # الانتظار في حال وجود حماية من التلغرام (Flood)
        await asyncio.sleep(e.seconds)
        return await unban_handler(event)
        
    except ChatAdminRequiredError:
        await event.respond("❌ خطأ: الحساب لا يملك صلاحيات 'حظر المستخدمين' هنا.")
        
    except Exception as e:
        # معالجة أي خطأ آخر بصمت أو برسالة بسيطة
        await event.respond(f"❌ لم أتمكن من إلغاء الحظر. السبب: {str(e)}")@ABH.on(events.NewMessage(pattern='del (.+)'))
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

