from ABH import *
# from shortcut import *
from telethon import Button
async def check_force_sub(user_id, channel_username):
    try:
        participant = await ABH.get_participants(channel_username, filter=lambda p: p.id == user_id)
        return True
    except Exception:
        return False
@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if not e.is_private:
        return
    if not await check_force_sub(e.sender_id, "x04ou"):
        b = Button.url('القناة', url='https://t.me/x04ou')
        return await e.reply("عذرا بس انت ما مشترك بالقناة")
    else:
        return await e.reply('تم التحقق من الاشتراك')
