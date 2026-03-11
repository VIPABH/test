import asyncio
from telethon import Button, events
from ABH import * # تأكد أن هذا الملف يحتوي على العميل 'ABH' واتصال 'r' (Redis)

async def check_force_sub(user_id, channel_username):
    """
    تحقق سريع من الاشتراك مع كاش (Cache) لمدة 120 ثانية.
    يعتمد على منطق get_permissions الأصلي الخاص بك.
    """
    cache_key = f"sub:{user_id}:{channel_username}"
    
    # 1. فحص الكاش (إذا وجد، يعني المستخدم مشترك مؤخراً)
    if r.exists(cache_key):
        return True
    
    try:
        # 2. منطق التحقق الأصلي الخاص بك (الذي طلبت عدم تغييره)
        await ABH.get_permissions(channel_username, user_id)
        
        # 3. إذا نجح التحقق، نحفظ الحالة في Redis لمدة دقيقتين (120 ثانية)
        r.setex(cache_key, 120, "1")
        return True
    except Exception:
        # في حال عدم الاشتراك أو وجود مشكلة، يعتبر غير مشترك
        return False



@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    # ضمان العمل في الخاص فقط
    if not e.is_private:
        return
    
    channel = "x04ou" 
    
    # تنفيذ التحقق باستخدام الدالة المطورة
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    # في حال كان مشتركاً
    await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')

