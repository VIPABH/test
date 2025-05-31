import os
import requests
from telethon import TelegramClient, events
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

IMAGE_FOLDER = "downloaded_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def fetch_images(query):
    # تحميل أول صورتين عبر استدعاء API خارجي أو سيرش
    # هذا مثال بسيط يحمّل رابط صورة ثابتة لتوضيح الفكرة فقط
    images = []
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/320px-A_small_cup_of_coffee.JPG"
    file_name = os.path.join(IMAGE_FOLDER, f"{query.replace(' ', '_')}_1.jpg")
    r = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(r.content)
    images.append(file_name)
    # لتجربة يمكنك تكرار الصورة أو إضافة صورة أخرى هنا
    images.append(file_name)
    return images

def compress_image(input_path, output_path, quality=40):
    img = Image.open(input_path)
    img = img.convert("RGB")
    img.save(output_path, "JPEG", optimize=True, quality=quality)

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
            await bot.send_file(event.chat_id, file=img_path, force_document=True, reply_to=event.id)

        for f in image_files + compressed_files:
            os.remove(f)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

print("🤖 البوت يعمل الآن...")
bot.run_until_disconnected()
