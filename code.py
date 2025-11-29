from telethon import events
from Resources import *
from ABH import ABH
@ABH.on(events.NewMessage)
async def handler(e):
    text = e.text
    x = create('audio_data.json')
    if text in x:
        info = x[text]
        await ABH.forward_messages(
            e.chat_id,
            info["message_id"],
            info.get("chat_id", e.chat_id)
        )
        return
    if text == "لطميات":
        data = ""
        for t, info in x.items():
            data += f"{t} → chat: {info.get('chat_id','N/A')}, msg_id: {info['message_id']}\n"
        await e.reply(data)
