import asyncio
import os
import aiohttp
from playwright.async_api import async_playwright
from pyppeteer import launch as py_launch
from ABH import *
# إعدادات المتصفح لـ Playwright (للسرعة القصوى)
pw_browser = None
pw_instance = None

async def get_pw():
    global pw_browser, pw_instance
    if not pw_browser:
        pw_instance = await async_playwright().start()
        pw_browser = await pw_instance.chromium.launch(headless=True)
    return pw_browser

# --- 1. محرك Playwright (الأسرع والأكثر استقراراً) ---
async def engine_playwright(url):
    browser = await get_pw()
    context = await browser.new_context(viewport={'width': 1280, 'height': 720})
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        path = f"pw_{os.urandom(2).hex()}.jpg"
        await page.screenshot(path=path, type="jpeg", quality=60)
        return path
    finally:
        await context.close()

# --- 2. محرك Pyppeteer (الأخف في استهلاك الرام) ---
async def engine_pyppeteer(url):
    browser = await py_launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 720})
    try:
        await page.goto(url, {'waitUntil': 'domcontentloaded'})
        path = f"py_{os.urandom(2).hex()}.jpg"
        await page.screenshot({'path': path, 'type': 'jpeg', 'quality': 60})
        return path
    finally:
        await browser.close()

# --- 3. محرك API الخارجي (الأسرع ولا يستهلك سيرفرك) ---
async def engine_api(url):
    # استخدام API ووردبريس السريع جداً والمجاني
    api_url = f"https://s.wordpress.com/mshots/v1/{url}?w=1280&h=720"
    path = f"api_{os.urandom(2).hex()}.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status == 200:
                with open(path, "wb") as f:
                    f.write(await resp.read())
                return path
    return None

# --- أمر التليجرام الرئيسي ---
@ABH.on(events.NewMessage(pattern=r'/(pw|py|api)\s+(.*)'))
async def multi_engine_shot(event):
    engine_type = event.pattern_match.group(1) # سيعرف إذا اخترت pw أو py أو api
    url = event.pattern_match.group(2)
    
    if not url.startswith("http"): url = "https://" + url
    
    msg = await event.reply(f"🔍 جاري الفحص باستخدام محرك: **{engine_type.upper()}**...")
    
    path = None
    if engine_type == "pw":
        path = await engine_playwright(url)
    elif engine_type == "py":
        path = await engine_pyppeteer(url)
    elif engine_type == "api":
        path = await engine_api(url)
        
    if path and os.path.exists(path):
        await event.reply(f"✅ تم بنجاح عبر {engine_type.upper()}", file=path)
        os.remove(path)
    else:
        await event.reply("❌ فشل المحرك في التقاط الصورة.")
    
    await msg.delete()
