from telethon import TelegramClient, events, connection, Button
# from shortcut import *
from ABH import *
import asyncio
channels = [
    'ANYMOUSupdate', 
    'x04ou'
]
async def is_in_channel(user_id, channel_username):
    try:
        return await ABH(GetParticipantRequest(channel_username, user_id))
    except:
        return False

@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    uid = e.sender_id
    results = await asyncio.gather(
        *(is_in_channel(uid, ch) for ch in channels)
    )
    buttons = []
    for (ch, link), joined in zip(channels.items(), results):
        if not joined:
            buttons.append([Button.url(f"اشترك في {ch}", link)])
    if buttons:
        await e.reply(
            "🔐 للوصول إلى خدمات البوت يجب الاشتراك في القنوات التالية:",
            buttons=buttons
        )
    else:
        await e.reply("✅ تم التحقق من اشتراكك في جميع القنوات. أهلاً بك!")
