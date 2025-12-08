from Resources import mention
from telethon import events
from ABH import ABH
import random, asyncio
killamordersession = {}
@ABH.on(events.NewMessage(pattern='(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    id = e.sender_id
    if chat in killamordersession:
        await e.reply('اللعبة مشتغله مسبقا انتظرها تخلص')
        return
    m = await mention(e)
    killamordersession[chat] = {"owner": id, 'players': {id: m}}
    await e.reply('اتم تشغيل لعبة القاتل والمقتول ارسل انا للانضمام')
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(e):
    chat_id = e.chat_id
    user_id = e.sender_id
    if chat_id not in killamordersession:
        killamordersession[chat_id] = {'players': {}}
    players = killamordersession[chat_id]['players']
    if user_id in players:
        await e.reply('سجلتك مسبقًا ✅')
    else:
        m = await mention(e)  
        players[user_id] = m
        await e.reply(f'تم تسجيلك كلاعب: {m}')
@ABH.on(events.NewMessage(pattern='اللاعبين'))
async def useless(e):
    chat = e.chat_id
    msg = 'اللاعبين 👇\n'
    if chat in killamordersession and killamordersession[chat]["players"]:
        for id, m in killamordersession[chat]["players"].items():
            msg += f'اللاعب - ( {m} )\n'
        await e.reply(str(msg))
@ABH.on(events.NewMessage(pattern='تم'))
async def useless(e):
    chat = e.chat_id
    if chat in killamordersession and killamordersession[chat]["players"]:
        await e.reply('تم بدء اللعبه ')
        await asyncio.sleep(2)
        await set_auto_killer(e)
async def set_auto_killer(e):
    chat = e.chat_id
    players = list(killamordersession[chat]["players"].keys())
    player = random.choice(players)
    m = killamordersession[chat]['players'][player]
    await e.reply(f"عزيزي ( {m} ) انت القاتل ")
