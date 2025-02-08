from telethon import TelegramClient, events
from playwright.async_api import async_playwright
import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

BANNED_SITES = [
    "porn", "xvideos", "xnxx", "redtube", "xhamster",
    "brazzers", "youjizz", "spankbang", "erotic", "sex"
]

DEVICES = {
    "pc": {"width": 1920, "height": 1080, "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    "iphone": "iPhone 13",
    "android": "Samsung Galaxy S21"
}

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def is_safe_url(url):
    return not any(banned in url.lower() for banned in BANNED_SITES)

async def take_screenshot(url, device="pc"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if device in DEVICES:
            if isinstance(DEVICES[device], str):
                device_preset = p.devices[DEVICES[device]]
                await page.set_viewport_size(device_preset["viewport"])
                await page.set_user_agent(device_preset["user_agent"])
            else:
                await page.set_viewport_size({"width": DEVICES[device]["width"], "height": DEVICES[device]["height"]})
                await page.set_user_agent(DEVICES[device]["user_agent"])

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            screenshot_path = f"screenshot_{device}.png"
            await page.screenshot(path=screenshot_path)
        
        except Exception as e:
            print(f"❌ خطأ أثناء تحميل الصفحة: {e}")
            screenshot_path = None
        
        finally:
            await browser.close()

    return screenshot_path

@client.on(events.NewMessage(pattern='/دز (.+) (pc|iphone|android)?'))
async def handler(event):
    match = event.pattern_match.groups()
    url = match[0]
    device = match[1] if match[1] else "pc"

    if not is_safe_url(url):
        await event.reply("🚫 هذا الموقع محظور! جرب تتواصل مع المطور @k_4x1")
        return

    screenshot_path = await take_screenshot(url, device)

    if screenshot_path:
        await event.reply(f'📸 تم التقاط لقطة الشاشة لجهاز **{device}**:', file=screenshot_path)
    else:
        await event.reply("❌ هنالك خطأ أثناء التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")

print("✅ البوت يعمل... انتظر الأوامر!")
client.run_until_disconnected()
