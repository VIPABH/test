from telethon import TelegramClient, events
from ABH import ABH as bot
# 1. الترحيب عند انضمام عضو جديد أو إضافة البوت للجروب
@bot.on(events.ChatAction)
async def handler(event):
    if event.user_joined or event.user_added:
        # معرفة البوت نفسه
        me = await bot.get_me()
        
        # إذا كان العضو المضاف هو البوت نفسه
        if me.id in event.user_ids:
            await event.respond("شكراً لإضافتي إلى المجموعة! 🤖✨\nأنا جاهز للعمل الآن.")
        else:
            # إذا كان المضاف عضواً جديداً
            for user in event.users:
                # تجنب الترحيب بالبوتات الأخرى
                if not user.bot:
                    await event.respond(f"أهلاً بك يا [{user.first_name}](tg://user?id={user.id}) في الجروب! 🌹")

# 2. الترحيب عند ترقية البوت إلى مشرف (Admin)
@bot.on(events.Raw)
async def raw_handler(event):
    # التحرّي عن التغييرات في صلاحيات القناة/الجروب
    from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
    
    if isinstance(event, UpdateChannelParticipant):
        me = await bot.get_me()
        # إذا كانت الترقية تخص البوت نفسه
        if event.user_id == me.id and isinstance(event.new_participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            await bot.send_message(
                event.channel_id,
                "تم ترقيتي إلى مشرف بنجاح! 👑\nشكراً لكم على الثقة."
            )

print("البوت يعمل الآن عبر Telethon...")
