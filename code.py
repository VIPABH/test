from telethon import events
from Resources import *
from ABH import ABH
from rapidfuzz import fuzz, process
@ABH.on(events.NewMessage)
async def handler(e):
    text = e.text
    x = create('audio_data.json')
    keys = list(x.keys())
    match, score, idx = process.extractOne(text, keys, scorer=fuzz.partial_ratio)
    if score >= 70:
        info = x[match]
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
