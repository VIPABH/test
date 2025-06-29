from telethon.tl.functions.users import GetFullUserRequest
from telethon import events
from ABH import ABH


@ABH.on(events.NewMessage(pattern='^نبذتي$'))
async def get_bio(event):
    try:
        # جلب البيانات الكاملة للمستخدم (بما فيها النبذة)
        full_user = await event.client(GetFullUserRequest(event.sender_id))
        
        if full_user.about:  # النبذة مخزنة في `about` وليس `bio`
            await event.reply(f"نبذتك:\n`{full_user.about}`")
        else:
            await event.reply("⚠️ لا يوجد لديك نبذة!")
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {e}")
