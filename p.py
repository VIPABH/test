from telethon import TelegramClient, events
import os, asyncio, random, time

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

if not all([api_id, api_hash, bot_token]):
    raise ValueError("الرجاء ضبط المتغيرات البيئية API_ID, API_HASH, و BOT_TOKEN")

ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

players = {}
answer = None
is_on = False
start_time = None
words = [
    'علي', 'حميد', 'العظيم', 'المجيد', 'مهندس', 'لاعب', 'صانع', 'كلمة',
    'مفردة', 'مبارك', 'مبرمج', 'الاول', 'مؤول', 'سميع', 'رحمن', 'طالب',
    'بطريق', 'سمع', 'يذهب', 'يعود', 'يقود', 'يرى', 'يكتب', 'الاسرع', 'كود',
    'نمط', 'تشغيل', 'خط', 'تاريخ', 'وقت', 'تجربة', 'جوهري', 'قاعدة', 'هروب',
]

@ABH.on(events.NewMessage(pattern="(?i)اسرع$"))
async def start_s(event):
    """بدء اللعبة والإعلان عنها"""
    global is_on, players
    is_on = True
    players.clear()
    await event.reply("تم بدء لعبة اسرع \nأرسل `انا` لدخول اللعبة أو `تم` للبدء.\n**ENJOY BABY✌**")

@ABH.on(events.NewMessage(pattern="(?i)انا$"))
async def sign_in(event):
    """تسجيل اللاعبين"""
    if is_on:
        uid = event.sender_id
        sender = await event.get_sender()
        name = sender.first_name
        if uid not in players:
            players[uid] = {"username": name}
            await event.reply('سجلتك بالعبة لتدز مره لخ')
        else:
            await event.reply("عزيزي الصديق ضفتك قبل شوية **ميحتاج تدز**")

@ABH.on(events.NewMessage(pattern="(?i)الاعبين$"))
async def players_show(event):
    """عرض قائمة اللاعبين"""
    if is_on:
        if players:
            player_list = "\n".join([f"{pid} - {info['username']}" for pid, info in players.items()])
            await event.reply(f"📜 قائمة اللاعبين:\n{player_list}")
        else:
            await event.reply('ماكو لاعبين 🙃')

@ABH.on(events.NewMessage(pattern="(?i)ابدا$"))
async def start_f(event):
    """بدء الجولة واختيار الكلمة"""
    global answer, is_on, start_time
    if is_on:
        await event.reply('تم بدء اللعبه انتظر ثواني')
        await asyncio.sleep(2)
        answer = random.choice(words)
        await event.respond(f'✍ اكتب ⤶ `{answer}`')
        start_time = time.time()

@ABH.on(events.NewMessage)
async def check(event):
    """التحقق من الإجابة وإنهاء اللعبة"""
    global is_on, start_time, answer
    if not is_on or start_time is None:
        return
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time)
    milliseconds = int((elapsed_time - seconds) * 100)
    isabh = event.text.strip()
    uid = event.sender_id
    if answer and isabh.lower() == answer.lower() and uid in players:
        await event.reply(f'اجابة موفقة احسنت\n الوقت المستغرق {seconds}:{milliseconds}')
        is_on = False
        answer = None
        start_time = None
    elif elapsed_time >= 10:
        await event.reply('انتهت المدة ومحد جاووب🥱')
        is_on = False
        answer = None
        start_time = None

ABH.run_until_disconnected()
