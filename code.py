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
from telethon.tl.types import ChatBannedRights, Channel, Chat
from telethon.errors import FloodWaitError, ChatAdminRequiredError, UserAdminInvalidError
import asyncio

# دالة فك الحظر (بالرد أو بالمعرف)
@ABH.on(events.NewMessage(pattern=r'/unban(?: (\d+))?'))
async def unban_handler(event):
    user_id = None
    
    # 1. جلب الـ ID سواء من الرد أو من الرقم المكتوب
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
    elif event.pattern_match.group(1):
        user_id = int(event.pattern_match.group(1))
    
    if not user_id:
        return await event.respond("⚠️ يرجى الرد على رسالة المستخدم أو كتابة الـ ID الخاص به.")

    try:
        # 2. الحصول على كيان الدردشة
        chat_entity = await event.get_chat()

        # 3. الطريقة الأكثر استقراراً لفك الحظر في Telethon
        # نرسل كائن حقوق فارغ تماماً (كل شيء مسموح)
        await ABH.edit_permissions(
            chat_entity,
            user_id,
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
        
        await event.respond(f"✅ تم بنجاح فك الحظر/القيود عن: `{user_id}`")

    except ValueError:
        # هذا هو حل مشكلة "You must pass either a channel or a supergroup"
        # للمجموعات العادية: نقوم بإزالة المستخدم من قائمة المحظورين عبر إزالته من الدردشة (إجراء شكلي لفك الحظر)
        try:
            from telethon.tl.functions.messages import DeleteChatUserRequest
            await ABH(DeleteChatUserRequest(event.chat_id, user_id))
            await event.respond(f"✅ تم فك حظر المستخدم من المجموعة العادية.")
        except Exception as e:
            await event.respond(f"❌ فشل فك الحظر في المجموعة العادية: {str(e)}")

    except ChatAdminRequiredError:
        await event.respond("❌ خطأ: الحساب لا يملك صلاحيات مسؤول (حظر الأعضاء).")
    except UserAdminInvalidError:
        await event.respond("❌ لا يمكنني تعديل صلاحيات هذا المستخدم (قد يكون مسؤولاً بالفعل).")
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await unban_handler(event)
    except Exception as e:
        await event.respond(f"❌ حدث خطأ غير متوقع: {str(e)}")
# تأكد من عدم وجود علامة @ ملتصقة بالأمر التالي
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

