from telethon import TelegramClient, events, Button
import requests, os, operator, asyncio, random
from googletrans import Translator
from bs4 import BeautifulSoup
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN') 
ABH = TelegramClient('c', api_id, api_hash).start(bot_token=bot_token)

players = {}
game_active = False

@ABH.on(events.NewMessage(pattern='^الافاعي$'))
async def start_game(event):
    global game_active, players
    if game_active:
        await event.reply("اللعبة جارية بالفعل!")
    else:
        game_active = True
        await event.reply("تم بدء لعبة الافاعي 🐍\nأرسل `انا` لدخول اللعبة.")
        asyncio.create_task(random_selection(event))

@ABH.on(events.NewMessage(pattern='^انا$'))
async def join_game(event):
    global game_active
    if not game_active:
        await event.reply("لا توجد لعبة جارية حاليًا. ابدأ لعبة جديدة بكتابة `الافاعي`.")
        return
    user_id = event.sender_id
    if user_id not in players:
        players[user_id] = {'name': event.sender.first_name}
        await event.reply(f"تم تسجيلك في اللعبة، {event.sender.first_name}!")
    else:
        await event.reply("أنت مسجل بالفعل في اللعبة.")
@ABH.on(events.NewMessage(pattern='ابدا'))
async def random_selection(event):
    global game_active, players
    while game_active:
        await asyncio.sleep(30)
        if not players:
            game_active = False
            return
        if len(players) == 1:
            winner_id = list(players.keys())[0]
            winner_name = players[winner_id]['name']
            await event.reply(f"تهانينا! اللاعب {winner_name} هو الفائز 🎉🐍!")
            game_active = False
            players = {}
            return
        random_player_id = random.choice(list(players.keys()))
        random_player_name = players[random_player_id]['name']
        await event.reply(f"انتقل اللاعب {random_player_name} إلى رحمة الله 🪦\nسبب الوفاة: عضته حية 🐍")
        del players[random_player_id]
        if len(players) == 1:
            winner_id = list(players.keys())[0]
            winner_name = players[winner_id]['name']
            await event.reply(f"الاعب {winner_name} نجى من الموت ب اعجوبة \n شكد فكر")
            game_active = False
            players = {}
print("Bot is running...")
asyncio.run(asyncio.sleep(5))
