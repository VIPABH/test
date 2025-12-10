from telethon import events, Button
from Resources import mention
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
@ABH.on(events.NewMessage(pattern='تم', incoming=True))
async def useless(e):
    chat = e.chat_id
    if chat in killamordersession and killamordersession[chat]["players"]:
        await e.reply('يتم بدء اللعبه ')
        # await asyncio.sleep(2)
        much = len(killamordersession[chat]['players'])
        for _ in range(much):
            await set_auto_killer(e)
async def set_auto_killer(e):
    chat = e.chat_id
    much = killamordersession[chat]['players']
    players = list(much.items())
    player, _ = random.choice(players)
    killamordersession[chat]['killer'] = player
    m = killamordersession[chat]['players'][player]
    b = [Button.inline('تحديد الضحية', data="choice_to_kill"), Button.inline('قتل عشوائي', data="autokill")]
    await e.reply(f"عزيزي ( {m} ) انت القاتل ", buttons=b)
    await asyncio.sleep(7)
    if len(much) == 1:
        for id, m in killamordersession[chat]['players'].items():
            await e.reply(f'مبارك للاعب ( {m} ) فاز اللعبة')
            del killamordersession[chat]
@ABH.on(events.CallbackQuery)
async def useless(e):
    chat = e.chat_id
    id = e.sender_id
    killer = killamordersession[chat]['killer']
    if killer and id != killer:
        return
    data = e.data.decode('utf-8')
    if not data in ('autokill', 'choice_to_kill'):
        return
    players = list(killamordersession[chat]["players"].items())
    if data == 'autokill':
        player, m = random.choice(players)
        del killamordersession[chat]["players"][player]
        if player == killer:
            await e.reply(f'انتحر اللاعب ( {m} ) جان مختل عقليا للاسف')
            del killamordersession[chat]['killer']
            return
        await e.edit(f'انتقل الى رحمة الله اللاعب ( {m} )')
        del killamordersession[chat]['killer']from telethon import events, Button
from Resources import mention
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
@ABH.on(events.NewMessage(pattern='تم', incoming=True))
async def useless(e):
    chat = e.chat_id
    if chat in killamordersession and killamordersession[chat]["players"]:
        await e.reply('يتم بدء اللعبه ')
        # await asyncio.sleep(2)
        much = len(killamordersession[chat]['players'])
        for _ in range(much):
            await set_auto_killer(e)
async def set_auto_killer(e):
    chat = e.chat_id
    much = killamordersession[chat]['players']
    players = list(much.items())
    player, _ = random.choice(players)
    killamordersession[chat]['killer'] = player
    m = killamordersession[chat]['players'][player]
    b = [Button.inline('تحديد الضحية', data="choice_to_kill"), Button.inline('قتل عشوائي', data="autokill")]
    await e.reply(f"عزيزي ( {m} ) انت القاتل ", buttons=b)
    await asyncio.sleep(7)
    if len(much) == 1:
        for id, m in killamordersession[chat]['players'].items():
            await e.reply(f'مبارك للاعب ( {m} ) فاز اللعبة')
            del killamordersession[chat]
@ABH.on(events.CallbackQuery)
async def useless(e):
    chat = e.chat_id
    id = e.sender_id
    killer = killamordersession[chat]['killer']
    if killer and id != killer:
        return
    data = e.data.decode('utf-8')
    if not data in ('autokill', 'choice_to_kill'):
        return
    players = list(killamordersession[chat]["players"].items())
    if data == 'autokill':
        player, m = random.choice(players)
        del killamordersession[chat]["players"][player]
        if player == killer:
            await e.reply(f'انتحر اللاعب ( {m} ) جان مختل عقليا للاسف')
            del killamordersession[chat]['killer']
            return
        await e.edit(f'انتقل الى رحمة الله اللاعب ( {m} )')
        del killamordersession[chat]['killer']
