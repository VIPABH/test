from telethon import TelegramClient, events
import redis, os
import os
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
user = TelegramClient('user', api_id, api_hash)
r = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
CHANNEL_KEY = 'anymousupdate'
ch = r.get(CHANNEL_KEY)
buttons = Button.url('🫆', url=f'https://t.me/{ch}')
async def chs(event, c):
    await ABH.send_message(event.chat_id, c, reply_to=event.id, buttons=buttons)
