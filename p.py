import os
import asyncio
from telethon import TelegramClient, events
from playwright.async_api import async_playwright

API_ID = int(os.getenv('API_ID', '123456'))
API_HASH = os.getenv('API_HASH', 'your_api_hash')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')
BOT = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# مسار لحفظ الصور
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# الدالة التي تلتقط السكرين كأنها من iPhone
async def screenshot_as_iphone(url, filename):
    async with async_playwright() as p:
        iphone = p.devices['iPhone 13 Pro']
        browser = await p.webkit.launch()
        context = await browser.new_context(**iphone)
        page = await context.new_page()
        await page.goto(url)
        await page.screenshot(path=filename, full_page=True)
        await browser.close()

# أمر البوت: التقاط سكرين لرابط
@BOT.on(events.NewMessage(pattern=r'^سكرين (https?://[^\s]+)$'))
async def handler(event):
    url = event.pattern_match.group(1)
    file_name = os.path.join(SCREENSHOT_DIR, f"screenshot_{event.sender_id}.png")
    try:
        await event.reply("📸 جاري التقاط صورة الشاشة كأنها من iPhone ...")
        await screenshot_as_iphone(url, file_name)
        await BOT.send_file(event.chat_id, file_name, caption="✅ تم الالتقاط كأنها من iPhone 13 Pro")
        os.remove(file_name)  # حذف الصورة بعد الإرسال
    except Exception as e:
        await event.reply(f"❌ حدث خطأ: {str(e)}")

# تشغيل البوت
print("🤖 البوت يعمل الآن...")
BOT.run_until_disconnected()
