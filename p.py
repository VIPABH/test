from telethon import TelegramClient, events
import requests, json, os, asyncio

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
        res = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        if res.status_code == 200:
            return res.json().get("data", "ماكو رد واضح من الذكاء.")
        else:
            return "❌ صار خطأ بالسيرفر، جرب بعدين."
    except Exception as e:
        return f"⚠️ خطأ: {e}"

# إعداد Telethon
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern=r"^ذكاء\s*(.*)"))
async def ai_handler(event):
    user_q = event.pattern_match.group(1).strip()
    if not user_q:
        await event.reply("📝 اكتب سؤالك بعد كلمة 'ذكاء'.")
        return

    # إظهار حالة "يكتب الآن" بشكل متواصل لحد ما يجي الجواب
    async with event.client.action(event.chat_id, 'typing'):
        response = await asyncio.to_thread(ask_ai, user_q)

    # إرسال الرد بعد انتهاء حالة الكتابة
    await event.reply(response)

print("✅ البوت يعمل الآن.")
client.run_until_disconnected()
