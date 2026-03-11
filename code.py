from telethon import Button, events
from ABH import * # تأكد أن ABH يحتوي على client و r (اتصال Redis)

async def check_force_sub(user_id, channel_username):
    # مفتاح الكاش الخاص بالمستخدم
    cache_key = f"sub:{user_id}:{channel_username}"
    
    # 1. فحص الكاش (إذا كان موجوداً في Redis، فالمستخدم مشترك ومؤكد)
    if r.exists(cache_key):
        return True
    
    try:
        # 2. التحقق المباشر (طريقتك الأصلية التي لا نريد تغييرها)
        await ABH.get_permissions(channel_username, user_id)
        
        # 3. إذا نجح التحقق، نحفظ الحالة في Redis لمدة 120 ثانية فقط
        r.setex(cache_key, 120, "1")
        return True
    except Exception:
        # إذا فشل التحقق، نعتبره غير مشترك
        return False



@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    channel = "x04ou" 
    
    # استخدام الدالة مع نظام الكاش الذي أضفناه
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
