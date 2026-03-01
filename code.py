import asyncio
import os
from telethon import events
from playwright.async_api import async_playwright

# --- الإعدادات والقوائم السوداء ---
BANNED_SITES = ["porn", "xvideos", "xnxx", "redtube", "xhamster", "brazzers", "youjizz", "spankbang", "erotic", "sex"]
_BROWSER = None
_PW = None

async def init_browser():
    """تشغيل المتصفح مرة واحدة والبقاء في الذاكرة للسرعة"""
    global _BROWSER, _PW
    if not _BROWSER:
        _PW = await async_playwright().start()
        _BROWSER = await _PW.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    return _BROWSER

async def capture_device(browser, url, device_key):
    """وظيفة التقاط الصورة لجهاز محدد"""
    try:
        if device_key == "android":
            # محاكاة Galaxy S5
            context = await browser.new_context(**_PW.devices["Galaxy S5"])
        else:
            # إعدادات الـ PC
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            
        page = await context.new_page()
        # الانتقال للموقع مع انتظار تحميل الهيكل الأساسي فقط للسرعة
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        # سليب ثانية واحدة لضمان استقرار الصور (حسب طلبك)
        await asyncio.sleep(1)
        
        path = f"shot_{device_key}_{os.urandom(2).hex()}.jpg"
        await page.screenshot(path=path, type="jpeg", quality=60)
        await context.close()
        return path
    except Exception:
        return None

@ABH.on(events.NewMessage(pattern=r'كشف رابط|سكرين(?:\s*(.*))?'))
async def screen_shot(event):
    await botuse("سكرين") # استدعاء الإحصائيات الخاصة بك
    
    url = event.pattern_match.group(1)
    if not url:
        user_name = await username(event)
        url = f"https://t.me/{user_name}"
    
    # تصحيح الرابط وتدقيقه
    if not url.startswith("http"): url = "https://" + url
    if any(banned in url.lower() for banned in BANNED_SITES):
        return await event.reply("❌ هذا الموقع محظور!\nتواصل مع المطور: @k_4x1")

    # 1. إرسال رسالة التأكيد البدائية
    status_msg = await event.reply("🚀 جاري التقاط لقطات الشاشة (PC & Android)...")

    try:
        browser = await init_browser()
        
        # 2. تشغيل العمليتين في وقت واحد (Parallel) لتوفير الوقت
        tasks = [
            capture_device(browser, url, "pc"),
            capture_device(browser, url, "android")
        ]
        
        # انتظار النتائج معاً
        results = await asyncio.gather(*tasks)
        screenshot_paths = [p for p in results if p]

        if screenshot_paths:
            # 3. إرسال الصور دفعة واحدة
            caption = f"✅ تم الالتقاط بنجاح\n🔗 الرابط: {url}"
            await event.reply(caption, file=screenshot_paths)
            
            # تنظيف الملفات المؤقتة
            for path in screenshot_paths:
                if os.path.exists(path): os.remove(path)
        else:
            await event.reply("❌ فشل التقاط الصور، قد يكون الموقع محجوباً أو الرابط غير صحيح.")
            
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء المعالجة: `{str(e)}`")
    finally:
        # حذف رسالة التأكيد بعد الانتهاء
        await status_msg.delete()
