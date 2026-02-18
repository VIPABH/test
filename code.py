from telethon import events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import MessageEntityCustomEmoji, ReactionCustomEmoji
import requests, asyncio, json
from ABH import ABH
AI_SECRET = "AIChatPowerBrain123@2024"
def ask_ai(q):
    url = "https://powerbrainai.com/app/backend/api/api.php"
    headers = {
        "User-Agent": "Dart/3.3 (dart:io)",
        "Accept-Encoding": "gzip",
        "content-type": "application/json; charset=utf-8"
    }
    data = {
        "action": "send_message",
        "model": "gpt-4o-mini",
        "secret_token": AI_SECRET,
        "messages": [
            {"role": "system", "content": "ساعد باللهجة العراقية وكن ذكي وودود"},
            {"role": "user", "content": q}
        ]
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
    if res.status_code == 200:
        return res.json().get("data", "ماكو رد واضح من الذكاء.")
    else:
        return "صار خطأ بالسيرفر، جرب بعدين."
@ABH.on(events.NewMessage(pattern=r"^مخفي\s*(.*)"))
async def ai_handler(event):
        user_q = event.pattern_match.group(1)
        x = event.text
        async with event.client.action(event.chat_id, 'typing'):
            response = await asyncio.to_thread(ask_ai, user_q)
            if response:
                await event.reply(response)
