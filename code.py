from datetime import datetime
from telethon import events

@ABH.on(events.NewMessage(pattern='^(رسالة|رساله|وقت) (.+)$'))
async def gettime(e):
    # النص بعد الكلمة الأولى
    command = e.pattern_match.group(1)  # رساله، رسالة، أو وقت
    time_text = e.pattern_match.group(2) # نص الوقت، مثل 1:01

    # تحويل النص إلى ساعة ودقيقة
    try:
        target_time = datetime.strptime(time_text, "%H:%M").time()
    except ValueError:
        await e.reply("⚠️ صيغة الوقت غير صحيحة، استخدم HH:MM")
        return

    # البحث عن الرسائل في نفس الشات
    async for msg in ABH.iter_messages(e.chat_id, limit=1000):
        msg_time = msg.date.time()  # وقت الرسالة كـ time
        if msg_time.hour == target_time.hour and msg_time.minute == target_time.minute:
            # وجدنا أول رسالة في نفس الساعة والدقيقة
            await e.reply(f"📩 أول رسالة في {time_text}:\n\n{msg.text or '[ملف/ميديا]'}", reply_to=msg.id)
            return

    await e.reply(f"⚠️ لم يتم العثور على أي رسالة في الوقت {time_text}")
