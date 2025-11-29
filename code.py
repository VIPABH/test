from ABH import ABH
from telethon import events

x = {}

@ABH.on(events.NewMessage)
async def handler(e):

    # نفّذ عملية البحث فقط عندما تكون القائمة فارغة
    if not x:
        for i in range(50, 502):
            msg = await ABH.get_messages("x04ou", ids=i)

            if not msg or not msg.file:
                continue

            title = msg.file.title
            if not title:
                continue

            # الحصول على رابط مباشر بالطريقة الرسمية
            try:
                url = await ABH.get_download_url(msg)
            except:
                url = None

            x[title] = url

    # من هنا يبدأ نظام الرد
    text = e.text

    if text in x:
        await ABH.send_file(e.chat_id, x[text])

    elif text == "دز":
        await e.reply(str(x))
