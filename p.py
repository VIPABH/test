import random
from telethon import TelegramClient, events
import os
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
football = [
        {
            "answer": "الميعوف",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/c/2219196756/21013"
        },
        {
            "answer": "سالم الدوسري",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/54"
        },
        {
            "answer": "العويس",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/56"
        },
        {
            "answer": "علي البليهي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/58"
        },
        {
            "answer": "جحفلي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/60"
        },
        {
            "answer": "الشلهوب",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/62"
        },
        {
            "answer": "محمد البريك",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/64"
        },
        {
            "answer": "سعود",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/66"
        },
        {
            "answer": "ياسر الشهراني",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/70"
        },
        {
            "answer": "كريستيانو رونالدو",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/72"
        },
        {
            "answer": "امبابي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/74"
        },
        {
            "answer": "مودريتش",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/76"
        },
        {
            "answer": "بنزيما",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/78"
        },
        {
            "answer": "نيمار",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/80"
        },
        {
            "answer": "ميسي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/82"
        },
        {
            "answer": "راموس",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/84"
        },
        {
            "answer": "اشرف حكيمي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/86"
        },
        {
            "answer": "ماركينيوس",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/88"
        },
        {
            "answer": "محمد صلاح",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/90"
        },
        {
            "answer": "هازارد",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/92"
        },
        {
            "answer": "مالديني",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/94"
        },
        {
            "answer": "انيستا",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/96"
        },
        {
            "answer": "تشافي",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/98"
        },
        {
            "answer": "بيكيه",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/100"
        },
        {
            "answer": "بيل",
            "caption": "وش اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/102"
        },
        {
            "answer": "1995",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/104"
        },
        {
            "answer": "1997",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/106"
        },
        {
            "answer": "1998",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/108"
        },
        {
            "answer": "1999",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/110"
        },
        {
            "answer": "2002",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/112"
        },
        {
            "answer": "2005",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/114"
        },
        {
            "answer": "2007",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/116"
        },
        {
            "answer": "2008",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/118"
        },
        {
            "answer": "2009",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/120"
        },
        {
            "answer": "2000",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/122"
        },
        {
            "answer": "انشيلوتي",
            "caption": "وش اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/124"
        },
        {
            "answer": "مورينيو",
            "caption": "وش اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/126"
        },
        {
            "answer": "بيب غوارديولا",
            "caption": "وش اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/128"
        },
        {
            "answer": "هيرفي رينارد",
            "caption": "وش اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/130"
        },
        {
            "answer": "زيدان",
            "caption": "وش اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/132"
        }
]
user_state = {}
@ABH.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    r = random.choice(football)
    user_state[user_id] = {
        'answer': r['answer']
    }
    try:
        message_id = int(r['photo'].split("/")[-1])
        message = await ABH.get_messages("LANBOT2", ids=message_id)
        if message and message.media:
            file_path = await ABH.download_media(message.media)
            await ABH.send_file(event.chat_id, file_path, caption=r['caption'])
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await event.reply("❌ لم أتمكن من تحميل الصورة أو لا تحتوي على ميديا.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء تحميل الصورة: {e}")
@ABH.on(events.NewMessage)
async def answer_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    msg = event.raw_text.strip()
    if msg.startswith('/'):
        return
    if user_id in user_state:
        correct_answer = user_state[user_id]['answer']
        if msg == correct_answer:
            await event.reply("✅ إجابة صحيحة!")
        else:
            await event.reply("❌ إجابة خاطئة. حاول مرة أخرى.")
        del user_state[user_id]
ABH.run_until_disconnected()
