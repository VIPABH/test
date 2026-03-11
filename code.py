from telethon import Button, events
from ABH import * # تأكد أن ABH يحتوي على client و r (اتصال Redis)

async def check_force_sub(user_id, channel_username):
    """
    التحقق من الاشتراك مع كاش (Cache) لمدة دقيقتين (120 ثانية).
    """
    cache_key = f"sub:{user_id}:{channel_username}"
    
    # 1. التحقق من وجود الحالة في Redis
    if r.exists(cache_key):
        return True
    
    try:
        # 2. التحقق من تيليجرام مباشرة
        # get_permissions تنجح إذا كان المستخدم مشتركاً وتفشل (ترفع Exception) إذا لم يكن كذلك
        await ABH.get_permissions(channel_username, user_id)
        
        # 3. إذا نجح الطلب، نحفظ الحالة في Redis لمدة 120 ثانية
        r.setex(cache_key, 120, "1")
        return True
    except Exception:
        # أي خطأ يعني أن المستخدم ليس في القناة
        return False

@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    channel = "x04ou" 
    
    # التحقق من الاشتراك باستخدام نظام الكاش
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
