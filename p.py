from telethon import TelegramClient, events
import os, asyncio, random, time
api_id = os.getenv("API_ID")      
api_hash = os.getenv("API_HASH")  
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
players = {}
answer = None
is_on = False
words = [
    'علي',
    'حميد',
    'العظيم',
    'المجيد',
    'مهندس',
    'لاعب',
    'صانع',
    'كلمة',
    'مفردة',
    'مبارك',
    'مبرمج',
    'الاول',
    'مؤول',
    'سميع',
    'رحمن',
    'طالب',
    'بطريق',
    'سمع',
    'يذهب',
    'يعود',
    'يقود',
    'يرى',
    'يكتب',
    'الاسرع',
    'كود',
    'نمط',
    'تشغيل',
    'خط',
    'تاريخ',
    'وقت',
    'تجربة',
    'جوهري',
    'قاعدة',
    'هروب',
]
@ABH.on(events.NewMessage(pattern="اسرع"))
async def start_speed(event):
    global is_on
    is_on = True
    await event.reply("تم بدء لعبة اسرع \nأرسل `انا` لدخول اللعبة أو `تم` للبدء مع أو بدون لاعبين.\n**ENJOY BABY✌**")

@ABH.on(events.NewMessage(pattern="انا"))
async def sign_in(event):
    if is_on:
        id = event.sender_id
        sender = await event.get_sender()
        name = sender.first_name
        if id not in players:
            players[id] = {"username": name}
            await event.reply("تم تسجيلك في اللعبة!")
        else:
            await event.reply("عزيزي لتلح سجلتك تره😡")
@ABH.on(events.NewMessage(pattern="الاعبين"))
async def players_show(event):
    if is_on:
        if players:
            player_list = "\n".join([f"{pid} - {info['username']}" for pid, info in players.items()])
            await event.reply(f"قائمة اللاعبين:\n{player_list}")
        else:
            await event.reply("لا يوجد لاعبين مسجلين بعد!")
@ABH.on(events.NewMessage(pattern="ابدا"))
async def start_f(event):
    global answer, elapsed_time
    if is_on:
        await event.reply('تم بدء اللعبة جاري الاختيار')
        await asyncio.sleep(5)
        answer = random.choice(words)
        await event.respond(f'اكتب ⤶ {answer}')
start_time = time.time()
while True:
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time % 60)
    microseconds = int((elapsed_time - seconds) * 100)
    if elapsed_time >= 60:  
        break
    is_on = False
a = random.randit(3, 6)
@ABH.on(events.NewMessage)
async def check(event):
    global is_on
    isabh = event.text
    uid = event.sender_id
    if answer == isabh and is_on and uid in players:
        await event.reply(f'إجابة صحيحة! الوقت المستغرق: {seconds:02}:{microseconds:06}')
        is_on = False
    else:
        return
ABH.run_until_disconnected()
