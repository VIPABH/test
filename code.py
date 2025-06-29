from telethon.tl.types import InputPeerUser
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage('^صورتي$'))
async def mypic(event):
    s = await event.get_sender()
    photo = await event.client.download_profile_photo(
    InputPeerUser(user_id=s.id, access_hash=s.access_hash),
    file=f"user_{s.id}.jpg")
    await ABH.send_file(event.chat_id, file=photo, reply_to=event.id)
