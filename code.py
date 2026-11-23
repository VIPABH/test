from ABH import *
from Resources import *
target_bot_id = 2080276323
@ABH.on(events.NewMessage(from_users=target_bot_id))
async def _(e):
    await e.reply(str(e))
@ABH.on(events.MessageEdited)
async def resend_edited_media(event):
    msg = event.message
    if not msg.media:
        return
    if msg.out:
        return
    await ABH.send_file(
        event.chat_id,
        file=msg.media,
        caption=msg.text or "",
        reply_to=msg.id,
    )
