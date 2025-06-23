from telethon import events
from telethon.tl.custom import Conversation
from ABH import ABH
from Program import r
@ABH.on(events.NewMessage(pattern="^وضع رد$"))
async def reply_to_message(event):
    sender_id = event.sender_id
    async with ABH.conversation(sender_id, timeout=60) as conv:
        await conv.send_message("📝 أرسل الآن **اسم الرد** الذي تريد حفظه:")
        response = await conv.get_response()
        reply_name = response.text
        r.set(f'reply_{sender_id}', reply_name)
        await conv.send_message("📩 أرسل الآن محتوى الرد:\n(نص - صورة - فيديو - ملف - صوت)")
        response = await conv.get_response()
        if response.media:
            file = await response.download_media(file=f"media/{sender_id}_{reply_name}")
            r.set(f'reply_content_{sender_id}', file)
            r.set(f'reply_type_{sender_id}', "media")
            await conv.send_message(f"✅ تم حفظ الرد **{reply_name}** كوسيط: `{file}`")
        else:
            text = response.raw_text
            r.set(f'reply_content_{sender_id}', text)
            r.set(f'reply_type_{sender_id}', "text")
            await conv.send_message(f"✅ تم حفظ الرد **{reply_name}** كنص: {text}")
