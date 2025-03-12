from telethon import TelegramClient, events
import os
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
players = {}
is_on = False
@ABH.on(events.NewMessage('اسرع'))
async def start_speed(event):
    global is_on
    is_on = True
    await event.reply('تم بدء لعبة اسرع , ارسل `انا` لدخول اللعبة او `تم للبدء مع او بدون لاعبين\n **ENJOY BABY✌**`')
    id = event.sender_id
    name = event.sender.first_name
    players[id] = {'username': name}

@ABH.on(events.NewMessage(pattern='انا'))
async def sign_in(event):
    id = event.sender_id
    if is_on and id not in players:
        await event.reply('تم تسجيلك في اللعبة')
    else:
        return
@ABH.on(events.NewMessage(pattern='الاعبين'))
async def players_show(event):
    if is_on:
         await event.reply(f'الاعبين 👇 \n {players}')
         return
    
ABH.run_until_disconnected()
