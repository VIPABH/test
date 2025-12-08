from Resources import mention
from telethon import events
from ABH import ABH
killamorder = {}
@ABH.on(events.NewMessage(pattern='(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    id = e.sender_id
    if chat in killamorder:
        await e.reply('اللعبة مشتغله مسبقا انتظرها تخلص')
        return
    m = await mention(e)
    killamorder[chat] = {"owner": id, 'players': {id: m}}
    await e.reply('اتم بدء لعبة القاتل والمقتول ارسل انا للانضمام')
@ABH.on(events.NewMessage(pattern='انا'))
async def useless(e):
    chat = e.chat_id
    id = e.sender_id
    if chat in killamorder and id in killamorder[chat]["players"]:
        await e.reply('سجلتك مسبقا')
    else:
        m = await mention(e)
        killamorder[chat] = {'players': {id: m}}
@ABH.on(events.NewMessage(pattern='اللاعبين'))
async def useless(e):
    chat = e.chat_id
    msg = 'اللاعبين 👇\n'
    if chat in killamorder and killamorder[chat]["players"]:
        for id, m in killamorder[chat]["players"]:
            msg += f'اللاعب - ( {m} )'
        await e.reply(str(msg))
