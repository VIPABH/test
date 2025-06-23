from telethon import TelegramClient, events
import redis, os
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
r = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
