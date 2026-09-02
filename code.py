from telethon import events
from ABH import ABH as bot
@bot.on(events.ChatAction)
async def welcome_handler(event):
    me = await bot.get_me()    
    if event.is_admin and me.id in getattr(event, 'user_ids', []):
        await event.respond("تم ترقيتي إلى مشرف بنجاح! 👑\nشكراً لكم على الثقة.")
        return
    if event.user_joined or event.user_added:
        if me.id in event.user_ids:
            await event.respond("شكراً لإضافتي إلى المجموعة! 🤖✨\nأنا جاهز للعمل الآن.")
            return            
print("البوت يعمل الآن عبر Telethon...")
