from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage(pattern='ها'))
async def x(event):
    await event.respond("الرجاء إرسال معرف القناة:")
    response = await ABH.wait_for(events.NewMessage(from_user=event.sender_id))
    chanel = response.raw_text
    await event.reply(f'chanel={chanel}')
