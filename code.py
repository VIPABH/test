from telethon import events
from telethon.tl.types import (
    UpdateChannelParticipant,
    ChannelParticipantAdmin,
    ChannelParticipantCreator
)
from ABH import ABH as bot

@bot.on(events.Raw)
async def bot_monitor_handler(event):
    me = await bot.get_me()

    # 1. مراقبة ترقية البوت إلى مشرف (Admin)
    if isinstance(event, UpdateChannelParticipant):
        if event.user_id == me.id and isinstance(event.new_participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            await bot.send_message(
                event.channel_id,
                "تم ترقيتي إلى مشرف بنجاح! 👑\nشكراً لكم على الثقة."
            )
            return

    # 2. مراقبة إضافة البوت نفسه فقط إلى مجموعة جديدة
    if isinstance(event, events.ChatAction.Event):
        if (event.user_joined or event.user_added) and me.id in event.user_ids:
            await event.respond("شكراً لإضافتي إلى المجموعة! 🤖✨\nأنا جاهز للعمل الآن.")

print("البوت يراقب نفسه الآن عبر Telethon...")
