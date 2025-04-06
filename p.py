import os,json
from telethon import TelegramClient, events
api_id=os.getenv('API_ID')
api_hash=os.getenv('API_HASH')
bot_token=os.getenv('BOT_TOKEN')
ABH=TelegramClient('code',api_id,api_hash).start(bot_token=bot_token)
@ABH.on(events.MessageEdited)
async def test(event):
    await event.reply('ها شعدلت ولك')
ABH.run_until_disconnected()
