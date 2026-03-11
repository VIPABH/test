from telethon import Button, events
from ABH import *

async def check_force_sub(user_id, channel_username):
    try:
        # get_permissions تنجح إذا كان المستخدم عضواً وتفشل إذا لم يكن كذلك
        # هذا الطلب مباشر وسريع ولا يحتاج لجلب كامل قائمة المشتركين
        await ABH.get_permissions(channel_username, user_id)
        return True
    except Exception:
        # أي خطأ هنا يعني أن المستخدم غير مشترك أو حدث خطأ في الصلاحيات
        return False



@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    channel = "x04ou" 
    
    # التحقق المباشر بدون كاش
    if not await check_force_sub(e.sender_id, channel):
        return await e.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**",
            buttons=[[Button.url('اشترك في القناة', url=f'https://t.me/{channel}')]]
        )
    
    return await e.reply('✅ أهلاً بك، تم التحقق من اشتراكك بنجاح.')
