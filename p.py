import os
import time
import requests
from telethon import TelegramClient, events
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image

# إعدادات API تيليجرام من .env أو يمكنك وضعها مباشرة هنا
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

IMAGE_FOLDER = "downloaded_images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def compress_image(input_path, output_path, quality=50):
    try:
        img = Image.open(input_path)
        img = img.convert("RGB")
        img.save(output_path, "JPEG", optimize=True, quality=quality)
    except Exception as e:
        print(f"⚠️ خطأ في ضغط الصورة: {e}")

def fetch_pinterest_images(query):
    # إعداد خيارات كروم لتشغيل بدون واجهة
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    image_paths = []

    try:
        search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)  # انتظار تحميل الصفحة

        # محاولة جلب روابط أول صورتين من نتائج البحث
        images = driver.find_elements(By.XPATH, "//img[contains(@src, 'pinimg.com')]")[:5]
        count = 0
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("https://i.pinimg.com"):
                # تحميل الصورة
                img_data = requests.get(src).content
                file_name = os.path.join(IMAGE_FOLDER, f"{query.replace(' ', '_')}_{count+1}.jpg")
                with open(file_name, 'wb') as f:
                    f.write(img_data)
                image_paths.append(file_name)
                count += 1
                if count == 2:
                    break

    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب الصور من Pinterest: {e}")
    finally:
        driver.quit()

    return image_paths

@bot.on(events.NewMessage(pattern=r'^\.بنترست (.+)'))
async def pinterest_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن صور بنترست لـ: {query}")

    image_files = fetch_pinterest_images(query)
    if not image_files:
        await event.reply("⚠️ لم أتمكن من العثور على صور مناسبة.")
        return

    # ضغط الصور وإرسالها كرد
    compressed_files = []
    for img_path in image_files:
        compressed_path = img_path.replace(".jpg", "_compressed.jpg")
        compress_image(img_path, compressed_path)
        compressed_files.append(compressed_path)

    try:
        for img_path in compressed_files:
            await bot.send_file(event.chat_id, file=img_path, reply_to=event.id)
            time.sleep(1)
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

    # حذف الصور المؤقتة
    for f in image_files + compressed_files:
        if os.path.exists(f):
            os.remove(f)

bot.run_until_disconnected()
