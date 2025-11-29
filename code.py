from ABH import ABH
from telethon import events
import asyncio

x = {}

# تقسيم النص حسب الحد المسموح (4096)
async def send_in_chunks(chat_id, text):
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await ABH.send_message(chat_id, text[i:i+chunk_size])


async def get_url_safe(msg):
    # إعادة المحاولة 3 مرات
    for _ in range(3):
        try:
            url = await ABH.get_download_url(msg)
            if url:
                return url
        except:
            pass
        await asyncio.sleep(0.3)

    # إذا فشل كل شيء → fallback
    try:
        return f"tg://file?id={msg.media.document.id}"
    except:
        return None


@ABH.on(events.NewMessage)
async def handler(e):

    # نفّذ عملية البحث فقط عندما تكون القائمة فارغة
    if not x:
        for i in range(50, 502):
            msg = await ABH.get_messages("x04ou", ids=i)
            await asyncio.sleep(0.05)

            if not msg or not msg.file:
                continue

            title = msg.file.title
            if not title:
                continue

            url = await get_url_safe(msg)

            x[title] = url

    # من هنا يبدأ نظام الرد
    text = e.text

    if text in x:
        await ABH.send_file(e.chat_id, x[text])

    elif text == "دز":
        data = ""
        for k, v in x.items():
            data += f"{k} : {v}\n"

        await send_in_chunks(e.chat_id, data)
