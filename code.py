from telethon import Button, events
from ABH import *

# قمنا بتحويل اسم القناة إلى كائن Peer مرة واحدة عند بدء التشغيل
# لتقليل عمليات التحويل (Resolution) في كل مرة يتم فيها التحقق
CHANNEL_ENTITY = "x04ou" 

async def check_force_sub(user_id):
    try:
        # استخدام get_permissions مع entity القناة الثابت
        # هذا يختصر على المكتبة البحث عن القناة في كل مرة
        await ABH.get_permissions(CHANNEL_ENTITY, user_id)
        return True
    except:
        return False



@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    # التحقق المباشر
    if not await check_force_sub(e.sender_id):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{CHANNEL_ENTITY}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
