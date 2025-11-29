from telethon import events
from Resources import *
from ABH import ABH
@ABH.on(events.NewMessage)
async def handler(e):
    text = e.text
    x = create('audio_data.json')
    for title, info in x.items():
        if title.startswith(text):
            await ABH.forward_messages(e.chat_id, info["message_id"], info["chat_id"])
            return
    if text == "لطميات":
        data = ""
        for t, info in x.items():
            data += f"{t} → chat: {info['chat_id']}, msg_id: {info['message_id']}\n"
