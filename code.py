from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage(pattern='^نبذتي$'))  # الأمر الذي يستقبله البوت
async def get_bio(event):
    try:
        # جلب معلومات المستخدم
        user = await event.client.get_entity(event.sender_id)
        
        # التحقق من وجود نبذة
        bio = getattr(user, 'bio', None)  # إذا لم توجد نبذة، يرجع None
        
        if bio:
            await event.reply(f"نبذتك: \n`{bio}`")
        else:
            await event.reply("⚠️ لا يوجد لديك نبذة في الملف الشخصي!")
            
    except Exception as e:
        await event.reply(f"❌ حدث خطأ: {e}")
