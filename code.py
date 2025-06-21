from telethon import events
import random, asyncio
from ABH import ABH
@ABH.on(events.NewMessage(pattern="/extract"))
async def extract_file_id(event):
    channel = 'vipabh'
    message_id = 1204
    try:
        msg = await ABH.get_messages(channel, ids=message_id)
        if msg.media:
            file_id = msg.file.id
            await event.reply(f"تم استخراج File ID: `{file_id}`")
        else:
            await event.reply(" لم يتم العثور على ملف مرفق في هذه الرسالة.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ: {e}")
