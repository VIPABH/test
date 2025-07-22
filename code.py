from telethon.tl.types import MessageEntityUrl
from telethon import events, Button
from ABH import ABH #type:ignore
from Resources import *
import asyncio
report_data = {}
@ABH.on(events.MessageEdited)
async def edited(event):
    if not event.is_group or not msg.edit_date:
        return
    msg = event.message
    chat_id = event.chat_id
    has_media = msg.media
    has_document = msg.document
    has_url = any(isinstance(entity, MessageEntityUrl) for entity in (msg.entities or []))
    if not (has_media or has_document or has_url):
        return
    uid = event.sender_id
    perms = await ABH.get_permissions(chat_id, uid)
    if perms.is_admin:
        return
    chat_obj = await event.get_chat()
    mention_text = await mention(event)
    if getattr(chat_obj, "username", None):
        رابط = f"https://t.me/{chat_obj.username}/{event.id}"
    else:
        clean_id = str(chat_obj.id).replace("-100", "")
        رابط = f"https://t.me/c/{clean_id}/{event.id}"
    report_data[event.id] = uid
    buttons = [
        [
            Button.inline(' نعم', data=f"yes:{uid}"),
            Button.inline(' لا', data=f"no:{uid}")
        ]
    ]
    await ABH.send_message(
        int(wfffp),
        f""" تم تعديل رسالة مشتبه بها:
 المستخدم: {mention_text}  
 [رابط الرسالة]({رابط})  
 معرفه: `{uid}`
 هل تعتقد أن هذه الرسالة تحتوي على تلغيم؟ 
 تاريخ النشر - {msg.date}
 تاريخ التعديل - {msg.edit_date}
 """,
        buttons=buttons,
        link_preview=True
    )
    await asyncio.sleep(60)
    await event.delete()
