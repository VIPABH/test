from telethon.tl.functions.users import GetFullUserRequest
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def get_bio(event):
    user = await event.client.get_entity(event.sender_id)
    if user.photo:
        avatar_path = await event.client.download_profile_photo(
            user,
            file=f"temp/avatar_{user.id}.jpg"
        )
    FullUser = (await event.client(GetFullUserRequest(event.sender_id))).full_user
    bio = FullUser.about
    bio_text = f"\n{bio}" if bio and bio.strip() else ""
    await ABH.send_file(event.chat_id, file= avatar_path, caption=bio_text,reply_to=event.id)
