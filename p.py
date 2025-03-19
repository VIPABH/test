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

# قائمة المواقع المحظورة
BANNED_SITES = [
    "porn", "xvideos", "xnxx", "redtube", "xhamster",
    "brazzers", "youjizz", "spankbang", "erotic", "sex"
]

# إعدادات الأجهزة
DEVICES = {
    "pc": {"width": 1920, "height": 1080, "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    "android": "Galaxy S5"
}

# دالة التقاط لقطة شاشة
async def take_screenshot(url, device="pc"):
    if not url:
        print("❌ خطأ: الرابط غير صالح.")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        if device in DEVICES:
            if isinstance(DEVICES[device], str):
                device_preset = p.devices.get(DEVICES[device])  # ✅ إصلاح الطريقة الجديدة لاستخدام الأجهزة
                if not device_preset:
                    print(f"❌ الجهاز '{device}' غير موجود في Playwright.")
                    return None
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

# استقبال الأمر وفحص الرابط والتقاط لقطة شاشة
@ABH.on(events.NewMessage(pattern=r'كشف رابط|سكرين (.+)'))
async def handler(event):
    match = event.pattern_match
    if not match or not match.group(1):
        await event.reply("❌ يرجى إدخال رابط صحيح.")
        return

    url = match.group(1).strip()
    
    if not url.startswith(("http://", "https://")):
        await event.reply("🚨 يجب أن يبدأ الرابط بـ `http://` أو `https://`.")
        return

    # التحقق من أن الرابط ليس من المواقع المحظورة
    if any(banned in url.lower() for banned in BANNED_SITES):
        await event.reply("🚫 هذا الموقع محظور! ❌")
        return

    devices = ['pc', 'android']
    screenshot_paths = []

    for device in devices:
        screenshot_path = await take_screenshot(url, device)
        if screenshot_path:
            screenshot_paths.append(screenshot_path)

    if screenshot_paths:
        await event.reply(f'✅ تم التقاط لقطات الشاشة للأجهزة التالية: **PC، Android**')
        for path in screenshot_paths:
            await event.respond(file=path)  # ✅ إرسال كل لقطة شاشة على حدة
    else:
        await event.reply("🙄 هنالك خطأ أثناء التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")

# تشغيل العميل إلى الأبد
ABH.run_until_disconnected()
