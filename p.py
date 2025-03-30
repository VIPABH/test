from telethon import TelegramClient, events
import os, asyncio
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
players = set()
join = False
@ABH.on(events.NewMessage(pattern='/vagueness|غموض'))
async def vagueness_start(event):
    global game, join
    await event.reply('تم بدء لعبة الغموض , يسجل الاعبين عبر امر `انا`')
    uid = event.sender_id
    if uid not in players:
        players.add(uid)
        return
    game = True
    join = True
@ABH.on(events.NewMessage(pattern='انا'))
async def me(event):
    if game and join:
        pid = event.sender_id
        players.add(pid)
        await event.reply('سجلتك , كول يا علي وانتظر')
    if pid in players:
        await event.reply('سجلتك من قبل😶')
        return
@ABH.on(events.NewMessage('تم'))
async def start_vagueness(event):
    global game, join
    join = False
    if len(players) < 2:
        await event.reply('اعتذر عن بدء اللعبة لكن العدد قليل')
        game = False
        join = False
        return
    else:
        await event.reply('تم الان اكملوا محادثتكم')
@ABH.on(events.NewMessage)
async def vagueness(event):
    sid = event.sender_id
    isrep = await event.get_reply_message()
    if sid in players and isrep:
        user = await event.client.get_entity(sid)
        nid = user.first_name
        await event.reply(f'العينتين {nid} سوه رد علئ رساله معينه وخسر 😁')
        players.discard(sid)
    if len(players) == 1:
        await event.reply('انتهت اللعبة فاز الاعب -> ')
ABH.run_until_disconnected
