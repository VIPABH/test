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

@ABH.on(events.NewMessage(pattern=r'forward')))
async def s(e):
    r = await e.get_reply_message()
    await ABH.forward_messages(GROUP_ID, r)
msg = None
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import FloodWaitError, ChatAdminRequiredError
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
        return await event.respond("⚠️ يرجى الرد على رسالة الشخص أو وضع الأيدي الخاص به.")

    # 2. إعداد حقوق "فارغة" (إلغاء كل أنواع الحظر والكتم)
    # ملاحظة: view_messages=False تعني أن المستخدم "غير ممنوع" من الرؤية
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
        # المحاولة الأولى: إلغاء الحظر المباشر
        await ABH(EditBannedRequest(GROUP_ID, user_id, unban_rights))
        
        # المحاولة الثانية (للضمان): استخدام دالة edit_permissions الشاملة
        # نجعل كل شيء True للسماح له بالدخول والمشاركة
        await ABH.edit_permissions(
            GROUP_ID, 
            user_id, 
            view_messages=True, 
            send_messages=True,
            send_media=True
        )
        
        await event.respond(f"✅ تم فك الحظر فعلياً عن `{user_id}`.\nيمكنه الآن الدخول للمجموعة.")

    except ChatAdminRequiredError:
        await event.respond("❌ لا أملك صلاحيات أدمن (حظر المستخدمين).")
    except Exception as e:
        # إذا كانت مجموعة عادية أو حدث خطأ في التوافق
        try:
            # الطريقة التقليدية: مسح القيود عبر المعرف المباشر
            from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
            await ABH.edit_permissions(GROUP_ID, user_id, view_messages=True)
            await event.respond(f"✅ تم فك قيود المستخدم `{user_id}`")
        except Exception as final_e:
            await event.respond(f"❌ فشل فك الحظر: {str(final_e)}")

    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await unban_handler(event)
@ABH.on(events.NewMessage(pattern=r'/del (.+)'))
async def delete_handler(event):
    # كود الحذف الخاص بك هنا
    message_ids = int(e.pattern_match.group(1))
    await ABH.delete_messages(GROUP_ID, message_ids)
    await hint(f"✅ Deleted messages with IDs: {message_ids}")
from telethon import events
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.errors import FloodWaitError
import asyncio

@ABH.on(events.NewMessage(pattern='fcb47'))
async def del_all_debug(e):
    try:
        # إرسال رسالة تنبيه بسيطة قبل الحذف
        await e.respond("🔄 جاري تنظيف المحادثة بالكامل...")
        
        # تنفيذ أمر مسح السجل (Clear History)
        # max_id=0 تعني حذف كل الرسائل بلا استثناء
        # just_clear=False تعني حذف الرسائل للجميع (إذا كنت أدمن)
        await ABH(DeleteHistoryRequest(
            peer=GROUP_ID   ,
            max_id=0,
            just_clear=False,
            revoke=True  # حذف الرسائل من عند الطرف الآخر أيضاً
        ))
        
    except FloodWaitError as error:
        # في حال طلب التلغرام الانتظار
        await asyncio.sleep(error.seconds)
        await del_all_debug(e)
        
    except Exception as error:
        # إذا حدث خطأ (مثلاً لست أدمن أو لا تملك الصلاحية)
        await e.reply(f"❌ لم أتمكن من مسح المحادثة: {str(error)}")
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
