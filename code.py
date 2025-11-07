from telethon import events
from ABH import *
@ABH.on(events.ChatAction)
async def on_chat_action(event):
    if event.user_joined:
        await event.reply("دخول")
    elif event.user_added:
        await event.reply("إضافة")
    elif event.user_left:
        await event.reply("مغادرة")
    elif getattr(event, "kicked_by", None):
        await event.reply("طرد")
    elif getattr(event, "new_admin_rights", None):
        await event.reply("رفع")
    elif getattr(event, "banned_rights", None):
        await event.reply("تقييد")
