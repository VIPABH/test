from telethon import types, events
from ABH import * 
@ABH.on(events.NewMessage(pattern="تيست"))
async def test(e):
    # جلب الرسالة التي رددت عليها
    r = await e.get_reply_message()
    if not r:
        await e.reply("يرجى الرد على رسالة.")
        return

    # استخدام get_messages مع خاصية reply_to لجلب الردود فقط
    # هذه الطريقة تجلب الرسائل التي تعتبر رسالتك هي الأصل لها
    replies = await e.client.get_messages(e.chat_id, reply_to=r.id)
    
    # الخاصية total في كائن الرسائل تجلب العدد الإجمالي من السيرفر
    count = replies.total
    
    await e.reply(f"عدد الردود الفعلي (طريقة البحث عن الردود) هو: {count}")
