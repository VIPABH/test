from telethon import Button, events

from ABH import *
async def check_force_sub(user_id, channel_username):
    # 1. فحص الكاش في Redis أولاً (لتقليل الـ API Calls)
    cache_key = f"sub:{user_id}:{channel_username}"
    if r.get(cache_key):
        return True
    
    try:
        # 2. استخدام get_permissions وهي أسرع بكثير من get_participants
        # لأنها تسأل فقط عن عضو واحد محدد
        participant = await ABH.get_permissions(channel_username, user_id)
        
        # إذا نجح الطلب، يعني المستخدم موجود -> حفظ الحالة في Redis لمدة 30 دقيقة
        r.setex(cache_key, 1800, "1")
        return True
    except:
        return False

@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    channel = "x04ou" # يوزر القناة
    
    # التحقق من الاشتراك
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
