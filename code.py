from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon import TelegramClient, events
from ABH import ABH as bot
@bot.on(events.ChatAction)
async def handler(event):
    if not event.user_joined or not event.user_added:return
    me = await bot.get_me()
    if not me.id in event.user_ids:return
    await event.respond("شكراً لإضافتي إلى المجموعة! 🤖✨\nأنا جاهز للعمل الآن.")
@bot.on(events.Raw)
async def raw_handler(event):
    if isinstance(event, UpdateChannelParticipant):
        me = await bot.get_me()
        if event.user_id == me.id and isinstance(event.new_participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            await bot.send_message(
                event.channel_id,
                "تم ترقيتي إلى مشرف بنجاح! 👑\nشكراً لكم على الثقة."
            )
print("البوت يعمل الآن عبر Telethon...")
