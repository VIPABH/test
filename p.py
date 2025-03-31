import os, json, random
from telethon import TelegramClient, events

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

def load_points(filename="points.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_points(data, filename="points.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

points = load_points()

def add_points(uid, gid, points_dict, amount=1):
    """إضافة نقاط لمستخدم معين داخل مجموعة معينة."""
    uid, gid = str(uid), str(gid)
    if uid not in points_dict:
        points_dict[uid] = {}
    if gid not in points_dict[uid]:
        points_dict[uid][gid] = {"points": 0}
    points_dict[uid][gid]["points"] += amount
    save_points(points_dict)

questions_and_answers_q = [
    {"question": "من هم ال البيت؟", "answer": ["هم اهل بيت رسول الله", 'اهل بيت رسول الله', "ال بيت رسول الله"]},
    {"question": "من هو الخليفة الاول؟", "answer": ["ابا الحسن علي", "الامام علي", "علي ابن ابي طالب"]},
]

user_states = {}

@ABH.on(events.NewMessage(pattern='اسئلة|/quist'))
async def start_question(event):
    """بدء السؤال العشوائي"""
    user_id = event.sender_id
    question = random.choice(questions_and_answers_q)
    user_states[user_id] = {
        "question": question,
        "waiting_for_answer": True
    }
    await event.reply(f"{question['question']}")

@ABH.on(events.NewMessage)
async def check_answer(event):
    """التحقق من إجابة المستخدم"""
    user_id = event.sender_id
    user_message = event.text.strip()
    gid = event.chat_id

    if user_id in user_states and user_states[user_id].get("waiting_for_answer"):
        current_question = user_states[user_id].get("question", {})
        correct_answers = current_question.get('answer', [])

        if user_message in correct_answers:
            add_points(user_id, gid, points, amount=1)
            await event.reply(f"هلا هلا طبوا الشيعة 🫡 \n نقاطك ↢ {points[str(user_id)][str(gid)]['points']}")
            del user_states[user_id]

ABH.run_until_disconnected()
