from ABH import ABH
from telethon import events
import asyncio

x = {}  # title -> link

async def send_in_chunks(chat_id, text):
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await ABH.send_message(chat_id, text[i:i+chunk_size])


@ABH.on(events.NewMessage)
async def handler(e):

    # البحث أول مرة فقط
    if not x:
        for i in range(50, 502):
            msg = await ABH.get_messages("x04ou", ids=i)
            await asyncio.sleep(0.05)

            if not msg or not msg.file:
                continue

            title = msg.file.title
            if not title:
                continue

            # رابط الرسالة الكامل
            x[title.lower()] = f"https://t.me/x04ou/{msg.id}"

    # متن الرسالة
    text = e.text.lower()

    # تطابق يبدأ من بداية الكلام فقط
    for title, link in x.items():
        if title.startswith(text):
            # إرسال الرسالة عبر الرابط
            await ABH.send_file(e.chat_id, link)
            return

    # إرسال القائمة
    if text == "دز":
        data = ""
        for t, link in x.items():
            data += f"{t} → {link}\n"
        await send_in_chunks(e.chat_id, data)
