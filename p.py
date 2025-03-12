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
async def start_s(event):
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
    global answer, is_on, start_time
    if is_on:
        await event.reply('تم بدء اللعبة جاري الاختيار')
        await asyncio.sleep(5)
        answer = random.choice(words)
        await event.respond(f'اكتب ⤶ {answer}')
        start_time = time.time()
@ABH.on(events.NewMessage)
async def check(event):
    global is_on, elapsed_time, answer, start_time
    if not is_on:
        return
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time % 60)
    microseconds = int((elapsed_time - seconds) * 1000000)
    isabh = event.text
    uid = event.sender_id
    if answer == isabh and uid in players:
        await event.reply(f'إجابة صحيحة! الوقت المستغرق: {seconds:02}:{microseconds:06}')
        is_on = False
        start_time = None
        answer = None
    elif elapsed_time >= 3:
        if is_on:
            await event.reply('انتهت المدة! لم يتم الإجابة في الوقت المحدد.')
            is_on = False
            start_time = None
            answer = None
ABH.run_until_disconnected()
