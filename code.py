from telethon.tl.types import InputPeerUser
from telethon import events
from ABH import ABH
import os

@ABH.on(events.NewMessage(pattern='^صورتي$'))
async def mypic(event):
    try:
        s = await event.get_sender()        
        full_user = await event.client.get_entity(s.id)
        photo = await event.client.download_profile_photo(
            s,
            file=f"temp_{s.id}.jpg"
        )
        if photo:
            bio_text = f"`{full_user.about}`" if hasattr(full_user, 'about') and full_user.about else "`لا يوجد وصف متاح`"
            await ABH.send_file(
                event.chat_id,
                file=photo,
                caption=bio_text,
                reply_to=event.id,
                parse_mode='md')
            os.remove(photo)
        else:
            await event.reply("⚠️ ليس لديك صورة ملف شخصي!")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ: {str(e)}")
        if 'photo' in locals() and os.path.exists(photo):
            os.remove(photo)
