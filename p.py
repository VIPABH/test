from telethon import TelegramClient, events
import os, asyncio, random

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
        players = {}  # تصفير اللاعبين عند بداية كل لعبة
        await event.reply("تم بدء لعبة الافاعي 🐍\nأرسل `انا` لدخول اللعبة.")

@ABH.on(events.NewMessage(pattern='^انا$'))
async def join_game(event):
    global game_active
    if not game_active:
        await event.reply("لا توجد لعبة جارية حاليًا. ابدأ لعبة جديدة بكتابة `الافاعي`.")
        return
    
    user_id = event.sender_id
    player_name = event.sender.first_name or "مجهول"
    
    if user_id not in players:
        players[user_id] = {'name': player_name}
        await event.reply(f"تم تسجيلك في اللعبة، {player_name}!")
    else:
        await event.reply("أنت مسجل بالفعل في اللعبة.")

@ABH.on(events.NewMessage(pattern='^ابدا$'))
async def run_random_selection(event):
    global game_active, players
    while game_active:
        await asyncio.sleep(7)
        
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
            await event.reply(f"اللاعب {winner_name} نجا من الموت بأعجوبة! 😱👏")
            game_active = False
            players = {}

print("Bot is running...")
ABH.run_until_disconnected()
