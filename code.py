from telethon.tl.types import InputPeerUser
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage(pattern='^صورتي$'))
async def mypic(event):
    s = await event.get_sender()
    e = await event.client.get_entity(s.id)
    photo = await event.client.download_profile_photo(
        InputPeerUser(user_id=s.id, access_hash=s.access_hash),
        file=f"user_{s.id}.jpg"
    )
    if photo:
        await ABH.send_file(
            event.chat_id,
            file=photo,
            caption=f"`{e.about}`",
            reply_to=event.id
        )
    else:
        await event.reply("⚠️ ليس لديك صورة ملف شخصي!")
