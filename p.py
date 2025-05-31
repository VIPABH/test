import os
import requests
from telethon import TelegramClient, events
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
serp_api_key = os.getenv("SERP_API_KEY")

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

IMAGE_FOLDER = "downloaded_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

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
                file_name = os.path.join(IMAGE_FOLDER, f"{query.replace(' ', '_')}_{len(images)+1}.jpg")
                with open(file_name, 'wb') as f:
                    f.write(img_data)
                images.append(file_name)
            except Exception as e:
                print(f"❌ خطأ في تحميل الصورة: {e}")

    return images

def compress_image(input_path, output_path, quality=70):
    try:
        img = Image.open(input_path)
        img = img.convert("RGB")  # تأكد من صيغة RGB
        img.save(output_path, "JPEG", optimize=True, quality=quality)
        print(f"✅ تم ضغط الصورة: {output_path}")
    except Exception as e:
        print(f"⚠️ خطأ في ضغط الصورة: {e}")

@bot.on(events.NewMessage(pattern=r'^\.صورة (.+)'))
async def handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن الصور لـ: {query}")

    try:
        image_files = fetch_images(query)
        if not image_files:
            await event.reply("⚠️ لم أتمكن من العثور على صور مناسبة.")
            return

        compressed_files = []
        for img_path in image_files:
            compressed_path = img_path.replace(".jpg", "_compressed.jpg")
            compress_image(img_path, compressed_path)
            compressed_files.append(compressed_path)

        for img_path in compressed_files:
            size_mb = os.path.getsize(img_path) / (1024 * 1024)
            print(f"حجم الصورة المضغوطة {img_path}: {size_mb:.2f} ميجابايت")
            await bot.send_file(event.chat_id, img_path, reply_to=event.id)

        # حذف الصور الأصلية والمضغوطة بعد الإرسال (اختياري)
        for f in image_files + compressed_files:
            os.remove(f)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

print("🤖 البوت يعمل الآن...")
bot.run_until_disconnected()
