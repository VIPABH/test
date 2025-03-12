from telethon import TelegramClient, events
import os

api_id = os.getenv("API_ID")      
api_hash = os.getenv("API_HASH")  
bot_token = os.getenv("BOT_TOKEN")

ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

players = {}
is_on = False

@ABH.on(events.NewMessage(pattern="اسرع"))
async def start_speed(event):
    global is_on
    is_on = True
    await event.reply("تم بدء لعبة اسرع \nأرسل `انا` لدخول اللعبة أو `تم` للبدء مع أو بدون لاعبين.\n**ENJOY BABY✌**")

@ABH.on(events.NewMessage(pattern="انا"))
async def sign_in(event):
    id = event.sender_id
    sender = await event.get_sender()
    name = sender.first_name

    if is_on and id not in players:
        players[id] = {"username": name}
        await event.reply("تم تسجيلك في اللعبة!")
    else:
        await event.reply("أنت مسجل بالفعل!")

@ABH.on(events.NewMessage(pattern="الاعبين"))
async def players_show(event):
    if is_on:
        if players:
            player_list = "\n".join([f"{pid} - {info['username']}" for pid, info in players.items()])
            await event.reply(f"قائمة اللاعبين:\n{player_list}")
        else:
            await event.reply("لا يوجد لاعبين مسجلين بعد!")

ABH.run_until_disconnected()
