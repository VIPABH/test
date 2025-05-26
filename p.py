from telethon import TelegramClient, events
import redis, os
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
r = redis.Redis(host='localhost', port=6379, db=0)
@ABH.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello! I am a bot that can store and retrieve data from Redis.')
    raise events.StopPropagation
@ABH.on(events.NewMessage(pattern='/set'))
async def set_data(event):
    if len(event.message.text.split()) < 3:
        await event.respond('Usage: /set key value')
        return
    key = event.message.text.split()[1]
    value = ' '.join(event.message.text.split()[2:])
    r.set(key, value)
    await event.respond(f'Set {key} to {value}')
    raise events.StopPropagation
@ABH.on(events.NewMessage(pattern='/get'))
async def get_data(event):
    if len(event.message.text.split()) < 2:
        await event.respond('Usage: /get key')
        return
    key = event.message.text.split()[1]
    value = r.get(key)
    if value is None:
        await event.respond(f'No value found for key {key}')
    else:
        await event.respond(f'Value for {key} is {value.decode("utf-8")}')
    raise events.StopPropagation
ABH.run_until_disconnected()
