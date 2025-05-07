from telethon import TelegramClient, events
import os, random, time

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

questions_and_answers_q = [
    {"question": "https://t.me/LANBOT2/90", "answer": "محمد صلاح"}
]
states = {}

@ABH.on(events.NewMessage(pattern='/start'))
async def quest(event):
    """بدء السؤال العشوائي"""
    user_id = event.sender_id
    quest = random.choice(questions_and_answers_q)
    states[user_id] = {
        "question": quest,
        "waiting_for_answer": True,
        "start_time": time.time()
    }

    # تحميل الصورة عبر ABH.download_media
    link = quest['question']
    try:
        # تحميل الرابط (الصورة) إلى ملف محلي
        downloaded_file = await ABH.download_media(link)

        if downloaded_file:  # التأكد من تحميل الملف بنجاح
            # إرسال الصورة بعد التحميل
            await event.reply(f"السؤال: من هو اللاعب الذي تم تصويره؟")
            await ABH.send_file(event.chat_id, downloaded_file, caption="إليك الصورة!")

        else:
            await event.reply("❌ فشل في تحميل الصورة.")
            
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء تحميل الصورة: {e}")

@ABH.on(events.NewMessage)
async def check_quist(event):
    if not event.text:
        return
    
    user_id = event.sender_id
    usermessage = event.text.strip()
    gid = event.chat_id
    
    if user_id in states and states[user_id].get("waiting_for_answer"):
        question_q = states[user_id].get("question", {})
        answers_q = [question_q.get('answer', '')]
        start_time = states[user_id].get("start_time")
        current_time = time.time()
        time_passed = current_time - start_time
        
        # تحقق من انقضاء الوقت
        if time_passed > 60:
            del states[user_id]
            return
        
        # تحقق من الإجابة الصحيحة
        if usermessage in answers_q:
            p = random.randint(50, 500)
            # يمكنك إضافة النقاط هنا عند الحاجة
            # add_points(user_id, gid, points, amount=p)
            await event.reply(
                f"✅ إجابة صحيحة! ربحت `{p}` نقاط!"
            )
            del states[user_id]
        else:
            await event.reply("❌ إجابة خاطئة. حاول مرة أخرى.")

ABH.run_until_disconnected()
