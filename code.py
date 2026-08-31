from ABH import ABH
from telethon.tl.custom import Button
@ABH.on(events.NewMessage)
async def _(e):
    await e.reply('>', buttons=[Button.mention('--', e.sender_id)])
