from telethon.tl.types import ForceReply
from telethon import TelegramClient, events 
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.NewMessage(pattern="^رفع مشرف.$"))
async def promote(event):
    await event.reply(
        "ارسل الصلاحيات",
        reply_markup=ForceReply(selective=True)
    )
