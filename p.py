import os
import random
from telethon import TelegramClient, events
from playwright.async_api import async_playwright  # ✅ إصلاح الاستيراد

# جلب البيانات من المتغيرات البيئية
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# التحقق من أن المتغيرات البيئية غير فارغة
if not all([api_id, api_hash, bot_token]):
    raise ValueError("❌ تأكد من تعيين API_ID, API_HASH, و BOT_TOKEN في المتغيرات البيئية.")

# تهيئة عميل تيليجرام
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
BANNED_SITES = [
    "porn", "xvideos", "xnxx", "redtube", "xhamster",
    "brazzers", "youjizz", "spankbang", "erotic", "sex"
]
DEVICES = {
    "pc": {"width": 1920, "height": 1080, "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    "android": "Galaxy S5"
}
def is_safe_url(url):
    return not any(banned in url.lower() for banned in BANNED_SITES)

async def take_screenshot(url, device="pc"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        if device in DEVICES:
            if isinstance(DEVICES[device], str):
                device_preset = p.devices[DEVICES[device]]
                context = await browser.new_context(**device_preset)
            else:
                context = await browser.new_context(
                    user_agent=DEVICES[device]["user_agent"],
                    viewport={"width": DEVICES[device]["width"], "height": DEVICES[device]["height"]}
                )
            page = await context.new_page()
        else:
            page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            screenshot_path = f"screenshot_{device}.png"
            await page.screenshot(path=screenshot_path)
        except Exception as e:
            print(f"❌ خطأ أثناء تحميل الصفحة: {e}")
            screenshot_path = None
        finally:
            await browser.close()
    return screenshot_path
@ABH.on(events.NewMessage(pattern=r'كشف رابط|سكرين (.+)'))
async def handler(event):
    url = event.pattern_match.group(1)
    if not is_safe_url(url):
        await event.reply("هذا الموقع محظور! \nجرب تتواصل مع المطور @k_4x1")
        return
    devices = ['pc', 'android']
    screenshot_paths = []
    for device in devices:
        screenshot_path = await take_screenshot(url, device)
        if screenshot_path:
            screenshot_paths.append(screenshot_path)
    if screenshot_paths:
        await event.reply(f' تم التقاط لقطات الشاشة للأجهزة التالية: **PC، Android**:', file=screenshot_paths)
    else:
        await event.reply("🙄 هنالك خطأ أثناء التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")
# تشغيل العميل إلى الأبد
ABH.run_until_disconnected()
