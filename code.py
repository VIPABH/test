from datetime import datetime
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage(pattern='^(رسالة|رساله|وقت) (.+)$'))
async def gettime(e):
    command = e.pattern_match.group(1)
    time_text = e.pattern_match.group(2)

    # تحويل الوقت
    try:
        target_time = datetime.strptime(time_text, "%H:%M").time()
    except ValueError:
        await e.reply("⚠️ صيغة الوقت غير صحيحة، استخدم HH:MM")
        return

    # البحث عن الرسائل
    async for msg in ABH.iter_messages(e.chat_id, limit=1000):
        msg_time = msg.date.time()
        if msg_time.hour == target_time.hour and msg_time.minute == target_time.minute:
            # تكوين الرابط
            if hasattr(e.chat, 'username') and e.chat.username:
                link = f"https://t.me/{e.chat.username}/{msg.id}"
            else:
                # للمجموعات الخاصة
                link = f"https://t.me/c/{str(e.chat_id)[4:]}/{msg.id}"
            await e.reply(f"📩 أول رسالة في {time_text}:\n{link}", reply_to=msg.id)
            return

    await e.reply(f"⚠️ لم يتم العثور على أي رسالة في الوقت {time_text}")
