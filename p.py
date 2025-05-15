from telethon import TelegramClient, events
import requests, json, os

AI_SECRET = "AIChatPowerBrain123@2024"

def ask_ai(q):
    try:
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
        res = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        if res.status_code == 200:
            return res.json()["data"]
        else:
            return "صار خطأ بالسيرفر، جرب بعدين."
    except Exception as e:
        return f"خطأ: {e}"

# إعداد Telethon
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')


client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# أمر ذكاء
@client.on(events.NewMessage(pattern=r"^ذكاء\s*(.*)", func=lambda e: e.is_group))
async def ai_handler(event):
    user_q = event.pattern_match.group(1).strip()
    if not user_q:
        await event.reply("اكتب سؤالك بعد كلمة 'ذكاء'.")
        return

    response = ask_ai(user_q)
    await event.reply(response)

print("البوت يعمل الآن.")
client.run_until_disconnected()
