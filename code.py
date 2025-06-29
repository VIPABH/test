from telethon.tl.functions.users import GetFullUserRequest
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def get_bio(event):
    FullUser = (await event.client(GetFullUserRequest(event.sender_id))).full_user
    bio = FullUser.about
    bio_text = f"\n{bio}" if bio and bio.strip() else ""
    await event.reply(bio_text)
