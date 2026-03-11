from ABH import *
# from shortcut import *
from telethon import Button
from telethon import Button, events, errors

async def check_force_sub(user_id, channel_username):
    try:
        # استخدام get_participant أسرع بآلاف المرات من get_participants
        await ABH.get_participant(channel_username, user_id)
        return True
    except errors.UserNotParticipantError:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    
    # التحقق من الاشتراك
    isSub = await check_force_sub(e.sender_id, "x04ou")
    
    if not isSub:
        # إضافة زر الاشتراك هو الجزء الأهم
        b = [Button.url('اشترك في القناة', url='https://t.me/x04ou')]
        await e.reply("عذراً، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", buttons=b)
    else:
        await e.reply('أهلاً بك! تم التحقق من اشتراكك بنجاح.')
