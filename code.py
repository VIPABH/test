from telethon.tl.types import InputPeerUser
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage(pattern='^صورتي$'))
async def mypic(event):
    # الحصول على معلومات المرسل
    s = await event.get_sender()
    
    # تحميل صورة الملف الشخصي
    photo = await event.client.download_profile_photo(
        InputPeerUser(user_id=s.id, access_hash=s.access_hash),
        file=f"user_{s.id}.jpg"
    )
    
    # إذا كان للمستخدم صورة ملف شخصي
    if photo:
        await ABH.send_file(
            event.chat_id,
            file=photo,  # هنا يجب استخدام المتغير `photo` بدلاً من `file`
            caption="ها هي صورتك!",
            reply_to=event.id
        )
    else:
        await event.reply("⚠️ ليس لديك صورة ملف شخصي!")
