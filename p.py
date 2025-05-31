from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from telethon import TelegramClient, events
import requests
import time
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء جلسة البوت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة تحميل أول صورتين من بحث الصور
def download_first_two_images(query):
    driver = webdriver.Chrome()  # تأكد من وجود chromedriver في نفس المجلد أو في PATH
    image_paths = []

    try:
        driver.get("https://www.google.com/imghp?hl=ar")

        # قبول الكوكيز إذا ظهرت
        try:
            consent_button = driver.find_element(By.XPATH, "//button[contains(., 'أوافق') or contains(., 'Accept all')]")
            consent_button.click()
        except:
            pass

        # تنفيذ البحث
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        # الحصول على أول صورتين
        images = driver.find_elements(By.XPATH, "//img[contains(@class, 'rg_i')]")[:2]
        for i, img in enumerate(images, start=1):
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if src:
                img_data = requests.get(src).content
                img_path = f"image_{i}.jpg"
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                image_paths.append(img_path)
                print(f"✅ تم تحميل الصورة {i}")

    finally:
        driver.quit()

    return image_paths

# التعامل مع أمر /صور
@bot.on(events.NewMessage(pattern=r'^/صور (.+)'))
async def handler(event):
    query = event.pattern_match.group(1)
    await event.reply("🔍 جاري البحث عن الصور ...")
    image_paths = download_first_two_images(query)

    if not image_paths:
        await event.reply("❌ لم يتم العثور على صور.")
        return

    for path in image_paths:
        await bot.send_file(
            entity=event.chat_id,
            file=path,
            reply_to=event.id
        )
        os.remove(path)

# تشغيل البوت
print("✅ البوت يعمل الآن.")
bot.run_until_disconnected()
