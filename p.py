from telethon import TelegramClient, events
import os, asyncio, random
api_id = os.getenv("API_ID")      
api_hash = os.getenv("API_HASH")  
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
players = {}
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

@ABH.on(events.NewMessage(pattern="الاعبين"))
async def players_show(event):
    if is_on:
        if players:
            player_list = "\n".join([f"{pid} - {info['username']}" for pid, info in players.items()])
            await event.reply(f"قائمة اللاعبين:\n{player_list}")
        else:
            await event.reply("لا يوجد لاعبين مسجلين بعد!")
@ABH.on(events.NewMessage(pattern="انا"))
async def start_f(event):
    global answer, is_on
    if is_on:
        await event.reply('تم بدء اللعبة جاري الاختيار')
        await asyncio.sleep(5)
        answer = random.choice(words)
        await event.respond(f'اكتب ⤶ {answer}')
@ABH.on(events.NewMessage)
async def check(event):
    if is_on:
        global is_on
    isabh = event.text
    if answer == isabh:
        await event.reply('احسنت جواب موفق')
        is_on = False
ABH.run_until_disconnected()
