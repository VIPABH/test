import os
import time
import requests
from telethon import TelegramClient, events
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# إعدادات API تيليجرام (ضع القيم في متغيرات بيئة أو مباشرة هنا)
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

IMAGE_FOLDER = "downloaded_images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def fetch_pinterest_images(query):
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

        # جلب أول 5 صور حقيقية من Pinterest
        images = driver.find_elements(By.XPATH, "//img[contains(@src, 'pinimg.com')]")[:5]
        count = 0
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("https://i.pinimg.com"):
                # تحميل الصورة بدقة كاملة (رابط src هو عادة صورة بحجم مناسب وجودة عالية)
                img_data = requests.get(src).content
                file_name = os.path.join(IMAGE_FOLDER, f"{query.replace(' ', '_')}_{count+1}.jpg")
                with open(file_name, 'wb') as f:
                    f.write(img_data)
                image_paths.append(file_name)
                count += 1
                if count == 2:  # أول صورتين فقط
                    break
    finally:
        driver.quit()

    return image_paths

@bot.on(events.NewMessage(pattern=r'^\.بنتر (.+)'))
async def pinterest_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن صور بنترست لـ: {query}")

    image_files = fetch_pinterest_images(query)
    if not image_files:
        await event.reply("⚠️ لم أتمكن من العثور على صور مناسبة.")
        return

    try:
        for img_path in image_files:
            # إرسال الصور بدقة كاملة بدون ضغط أو تعديل
            await bot.send_file(event.chat_id, file=img_path, reply_to=event.id)
            time.sleep(1)
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

    # حذف الصور المؤقتة بعد الإرسال
    for f in image_files:
        if os.path.exists(f):
            os.remove(f)

bot.run_until_disconnected()
