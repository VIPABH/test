from telethon import events
from telethon.tl.types import MessageActionChatAddUser, MessageActionChatJoinedByLink
from ABH import ABH as bot

@bot.on(events.ChatAction)
async def welcome_handler(event):
    me = await bot.get_me()

    # 1. حالة ترقية البوت إلى مشرف (Admin)
    if event.promoted and me.id in getattr(event, 'user_ids', []):
        await event.respond("تم ترقيتي إلى مشرف بنجاح! 👑\nشكراً لكم على الثقة.")
        return

    # 2. حالة إضافة البوت كعضو أو انضمام عضو جديد
    if event.user_joined or event.user_added:
        # إذا كان البوت نفسه هو المضاف
        if me.id in event.user_ids:
            await event.respond("شكراً لإضافتي إلى المجموعة! 🤖✨\nأنا جاهز للعمل الآن.")
            return

        # إذا كان الانضمام لعضو جديد (وليس بوت)
        for user in event.users:
            if not user.bot:
                await event.respond(f"أهلاً بك يا [{user.first_name}](tg://user?id={user.id}) في الجروب! 🌹")

print("البوت يعمل الآن عبر Telethon...")
