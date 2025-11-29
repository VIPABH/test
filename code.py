from ABH import ABH
from telethon import events
import asyncio
import json
import os

JSON_FILE = "audio_data.json"
x = {}  # title -> {"chat_id": ..., "message_id": ...}

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        x = json.load(f)

async def save_json():
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(x, f, ensure_ascii=False, indent=4)

async def send_in_chunks(chat_id, text):
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        await ABH.send_message(chat_id, text[i:i+chunk_size])

@ABH.on(events.NewMessage)
async def handler(e):

    # البحث أول مرة فقط إذا JSON فارغ
    if not x:
        for i in range(50, 502):
            msg = await ABH.get_messages("x04ou", ids=i)
            await asyncio.sleep(0.05)

            if not msg or not msg.file:
                continue

            title = msg.file.title
            if not title:
                continue

            x[title.lower()] = {
                "chat_id": "x04ou",
                "message_id": msg.id
            }

        await save_json()

    text = e.text.lower()

    # تطابق يبدأ من البداية
    for title, info in x.items():
        if len(title) > 2 and title.startswith(text):
            # إرسال الملف عن طريق forward_messages
            await ABH.forward_messages(e.chat_id, info["message_id"], info["chat_id"])
            return

    if text == "دز":
        data = ""
        for t, info in x.items():
            data += f"{t} → chat: {info['chat_id']}, msg_id: {info['message_id']}\n"
        await send_in_chunks(e.chat_id, data)
