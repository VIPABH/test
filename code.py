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
from telethon.tl.types import ChatBannedRights, Channel, Chat
from telethon.errors import FloodWaitError, ChatAdminRequiredError
import asyncio

# دالة فك الحظر
@ABH.on(events.NewMessage(pattern=r'/unban (\d+)'))
async def unban_handler(event):
    user_id = int(event.pattern_match.group(1))
    
    try:
        # الحصول على الكيان (Entity) للتأكد من نوع المجموعة
        entity = await event.get_chat()

        # إعداد حقوق "سماح بالكل"
        rights = ChatBannedRights(
            until_date=None,
            view_messages=False, # False يعني غير ممنوع من الرؤية (فك حظر)
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_links=False
        )

        if isinstance(entity, (Channel,)):
            # للمجموعات الخارقة والقنوات
            await ABH(EditBannedRequest(entity, user_id, rights))
            await event.respond(f"✅ تم فك الحظر (Supergroup/Channel) عن: `{user_id}`")
        
        elif isinstance(entity, Chat):
            # للمجموعات العادية: الحل هو حذف المستخدم من قائمة المحظورين
            # أو استخدام edit_permissions المبسطة للمجموعات
            try:
                await ABH.edit_permissions(entity.id, user_id, view_messages=True)
                await event.respond(f"✅ تم فك الحظر (Normal Group) عن: `{user_id}`")
            except Exception as e:
                await event.respond(f"⚠️ المجموعة عادية، يرجى دعوة المستخدم يدوياً.")
        
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await unban_handler(event)
    except ChatAdminRequiredError:
        await event.respond("❌ لا أملك صلاحيات أدمن لحظر/فك حظر المستخدمين.")
    except Exception as e:
        await event.respond(f"❌ خطأ غير متوقع: {str(e)}")

# تأكد من عدم وجود علامة @ ملتصقة بالأمر التالي
@ABH.on(events.NewMessage(pattern=r'/del (.+)'))
async def delete_handler(event):
    # كود الحذف الخاص بك هنا
    passasync def delete_message(e):
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

