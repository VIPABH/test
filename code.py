from ABH import *
# from shortcut import *
from telethon import Button
from telethon import Button, events, errors

from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant

async def check_force_sub(user_id, channel_username):
    try:
        # هذه الطريقة هي الأكثر كفاءة للتحقق من وجود عضو في قناة
        
        return await ABH(GetParticipantRequest(channel_username, user_id))
    except:
        return False
@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    # التحقق من الاشتراك
    isSub = await check_force_sub(e.sender_id, "x04ou")
    print(isSub)
    if not isSub:
        # إضافة زر الاشتراك هو الجزء الأهم
        b = [Button.url('اشترك في القناة', url='https://t.me/x04ou')]
        await e.reply("عذراً، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", buttons=b)
    else:
        await e.reply('أهلاً بك! تم التحقق من اشتراكك بنجاح.')
