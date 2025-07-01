from telethon.errors import MessageIdInvalidError
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def scan(event):
    channel_id = 'x04ou'
    for i in range(1, 386):
        try:
            msg = await ABH.get_messages(channel_id, ids=i)
            if msg and not msg.media:
                if msg.message:
                    await event.reply(f"رسالة [{i}]:\n{msg.message}")
                else:
                    await event.reply(f"رسالة [{i}] موجودة ولكن لا تحتوي على نص.")
        except MessageIdInvalidError:
            continue
        except Exception as e:
            await event.reply(f"حدث خطأ في الرسالة {i}:\n{str(e)}")
            continue
