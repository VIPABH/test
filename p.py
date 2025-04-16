from telethon import TelegramClient, events
import os, asyncio, random

api_id = int(os.getenv('API_ID'))      
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
        players = {}
        await event.reply("تم بدء لعبة الافاعي 🐍\nأرسل `انا` لدخول اللعبة.")
        asyncio.create_task(run_game(event))

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

async def run_game(event):
    global game_active, players
    await asyncio.sleep(30)  # مهلة أولية للسماح بالانضمام

    while game_active:
        if not players:
            await event.reply("لم ينضم أي لاعب. تم إنهاء اللعبة.")
            game_active = False
            return

        if len(players) == 1:
            winner_id = list(players.keys())[0]
            winner_name = players[winner_id]['name']
            await event.reply(f"🎉 تهانينا! اللاعب {winner_name} هو الفائز 🐍!")
            game_active = False
            players = {}
            return

        await asyncio.sleep(30)  # مهلة بين كل جولة
        eliminated_id = random.choice(list(players.keys()))
        eliminated_name = players[eliminated_id]['name']
        await event.reply(f"🪦 انتقل اللاعب {eliminated_name} إلى رحمة الله\nسبب الوفاة: عضته حية 🐍")
        del players[eliminated_id]

        if len(players) == 1:
            winner_id = list(players.keys())[0]
            winner_name = players[winner_id]['name']
            await event.reply(f"🎉 الاعب {winner_name} نجى من الموت بأعجوبة!\nشكد فكر 💡")
            game_active = False
            players = {}

print("🔄 Bot is running...")
ABH.run_until_disconnected()
