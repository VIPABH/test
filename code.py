from telethon import events
import os
from ABH import ABH

@ABH.on(events.NewMessage(pattern='^صورتي$'))
async def mypic(event):
    try:
        sender = await event.get_sender()
        user = await event.client.get_entity(sender.id)
        
        if user.photo:
            # Download the photo
            photo_path = await event.client.download_profile_photo(
                user,
                file=f"temp/user_{user.id}.jpg"
            )
            
            await event.client.send_file(
                event.chat_id,
                photo_path,
                caption=f"Bio: `{user.bio or 'No bio'}`",
                reply_to=event.id
            )
            
            # Clean up the downloaded file
            if os.path.exists(photo_path):
                os.remove(photo_path)
        else:
            await event.reply("⚠️ ليس لديك صورة ملف شخصي!")
            
    except Exception as e:
        await event.reply(f"❌ حدث خطأ: {str(e)}")
