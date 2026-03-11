from telethon import Button, events
from ABH import *

async def check_force_sub(user_id, channel_username):
    # مفتاح الكاش في Redis
    cache_key = f"sub:{user_id}:{channel_username}"
    
    # 1. التحقق من وجود المستخدم في الكاش
    if r.get(cache_key):
        return True
    
    try:
        # 2. التحقق من التيليجرام إذا لم يكن في الكاش
        await ABH.get_permissions(channel_username, user_id)
        
        # 3. إذا نجح، نحفظ الحالة في Redis لمدة 300 ثانية (5 دقائق)
        r.setex(cache_key, 300, "1")
        return True
    except Exception:
        return False

@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    channel = "x04ou" 
    
    # التحقق مع استخدام الكاش
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
