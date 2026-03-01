import asyncio
import os
import aiohttp
from telethon import events
from playwright.async_api import async_playwright
# تأكد من أن استيراد ABH صحيح في ملفك
# from ABH import * # --- إعدادات المتصفح العالمية ---
_BROWSER = None
_PW = None

async def init_browser():
    """تشغيل المتصفح مرة واحدة فقط لضمان السرعة القصوى"""
    global _BROWSER, _PW
    if not _BROWSER:
        _PW = await async_playwright().start()
        _BROWSER = await _PW.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
    return _BROWSER

# --- المحركات الذكية ---

async def engine_fast(url):
    """محرك سريع مع انتظار ثانية واحدة للاستقرار"""
    browser = await init_browser()
    context = await browser.new_context(viewport={'width': 1280, 'height': 720})
    page = await context.new_page()
    try:
        # الانتظار حتى تحميل الـ DOM (أفضل من commit للمواقع المتوسطة)
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        # الانتظار لمدة ثانية واحدة كما طلبت لضمان ظهور المحتوى
        await asyncio.sleep(1)
        
        path = f"fast_{os.urandom(2).hex()}.jpg"
        await page.screenshot(path=path, type="jpeg", quality=60)
        return path
    finally:
        await context.close()

async def engine_stealth(url):
    """محرك قوي يحاكي هاتف iPhone مع انتظار ثانية إضافية"""
    browser = await init_browser()
    context = await browser.new_context(**_PW.devices["iPhone 13 Pro Max"])
    page = await context.new_page()
    try:
        # الانتظار حتى سكون الشبكة تماماً
        await page.goto(url, wait_until="networkidle", timeout=25000)
        
        # ثانية إضافية لضمان تحميل الـ Javascript الثقيل
        await asyncio.sleep(1)
        
        path = f"full_{os.urandom(2).hex()}.jpg"
        await page.screenshot(path=path, type="jpeg", quality=80)
        return path
    finally:
        await context.close()

async def engine_api(url):
    """محرك خارجي - لا يحتاج sleep لأنه يعالج خارجياً"""
    api_url = f"https://s.wordpress.com/mshots/v1/{url}?w=1280&h=720"
    path = f"api_{os.urandom(2).hex()}.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status == 200:
                with open(path, "wb") as f:
                    f.write(await resp.read())
                return path
    return None

# --- الأوامر الرئيسية للبوت ---

@ABH.on(events.NewMessage(pattern=r'/(fast|full|api)\s+(.*)'))
async def multi_engine_shot(event):
    cmd = event.pattern_match.group(1).lower()
    url = event.pattern_match.group(2).strip()
    
    if not url.startswith("http"):
        url = "https://" + url

    status_msg = await event.reply(f"🚀 جاري المعالجة عبر محرك: **{cmd.upper()}**...")
    
    path = None
    try:
        if cmd == "fast":
            path = await engine_fast(url)
        elif cmd == "full":
            path = await engine_stealth(url)
        elif cmd == "api":
            path = await engine_api(url)

        if path and os.path.exists(path):
            caption = f"✅ **تم الالتقاط بنجاح**\n🔗 **الرابط:** {url}\n🛠 **المحرك:** {cmd.upper()}"
            await event.reply(caption, file=path)
            os.remove(path) 
        else:
            await event.reply("❌ فشل المحرك في جلب الصورة. جرب محركاً آخر.")
            
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ تقني: `{str(e)}`")
    finally:
        await status_msg.delete()
