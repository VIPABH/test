from telethon.tl.functions.channels import InviteToChannelRequest
from ABH import *
@ABH.on(events.NewMessage)
async def _(e):
    msg = await e.reply('.')
    await msg.pin()
