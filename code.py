from telethon import events, Button
from Resources import *
from ABH import ABH as clinet
import uuid, json
@client.on(events.NewMessage(pattern=r'^مخفي اختار'))
async def hidden_choice_handler(event):
    message = event.raw_text

    # استخراج جميع الاختيارات بالشكل: رقم - اختيار
    choices = re.findall(r"\d+\s*-\s*(.+)", message)

    if not choices:
        await event.reply("⚠️ لم يتم العثور على أي اختيارات.\nيرجى كتابة:\nمخفي اختار\n1- الصحة\n2- المال ...")
        return

    # اختيار عشوائي
    selected = random.choice(choices).strip()

    # إرسال النتيجة
    await event.reply(f"🎯 تم الاختيار العشوائي:\n👉 {selected}")
