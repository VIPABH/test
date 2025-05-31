import os
import requests
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
serp_api_key = "be7b31af3619fa5d4e50003df5da01e3f4008e4896731c2e746d33121f2ce942"

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def fetch_images(query):
    url = 'https://serpapi.com/search'
    params = {
        'q': query,
        'tbm': 'isch',
        'api_key': serp_api_key
    }

    res = requests.get(url, params=params)
    data = res.json()
    images = []

    for item in data.get("images_results", [])[:2]:
        img_url = item.get("original")
        if img_url:
            try:
                img_data = requests.get(img_url, timeout=10).content
                if len(img_data) > 4 * 1024 * 1024:  # تجاهل الصور الأكبر من 4 ميجابايت
                    continue
                file_name = f"{query.replace(' ', '_')}_{len(images)+1}.jpg"
                with open(file_name, 'wb') as f:
                    f.write(img_data)
                images.append(file_name)
            except Exception as e:
                print(f"❌ خطأ في تحميل الصورة: {e}")

    return images

@bot.on(events.NewMessage(pattern=r'^\.صورة (.+)'))
async def handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن: {query}")

    try:
        image_files = fetch_images(query)
        if not image_files:
            await event.reply("⚠️ لم أتمكن من العثور على صور مناسبة.")
            return
        for img in image_files:
            await bot.send_file(event.chat_id, img, reply_to=event.id)
            os.remove(img)
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

print("🤖 البوت يعمل...")
bot.run_until_disconnected()
