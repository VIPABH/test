from telethon import TelegramClient, events
from datetime import datetime, timedelta
import os, asyncio
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
games = {}
active_players = {}
running_tasks = set()
def format_duration(duration: timedelta) -> str:
    minutes, seconds = divmod(int(duration.total_seconds()), 60)
    return f"{minutes} دقيقة و {seconds} ثانية"
def reset_game(chat_id):
    if chat_id in games:
        del games[chat_id]
    if chat_id in active_players:
        del active_players[chat_id]
    running_tasks.discard(chat_id)
@ABH.on(events.NewMessage(pattern=r'^/(vagueness)$|^غموض$'))
async def vagueness_start(event):
    chat_id = event.chat_id
    games[chat_id] = {
        "players": set(),
        "player_times": {},
        "game_started": True,
        "join_enabled": True
    }
    active_players[chat_id] = set()
    await event.respond('🎮 تم بدء لعبة الغموض، يسجل اللاعبون عبر أمر `انا`')
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    game = games.get(chat_id)
    if not game or not game["game_started"] or not game["join_enabled"]:
        return
    if user_id in game["players"]:
        await event.respond('✅ أنت مسجل مسبقًا.')
        return
    game["players"].add(user_id)
    game["player_times"][user_id] = {"start": datetime.utcnow()}
    await event.respond('📝 تم تسجيلك، انتظر بدء اللعبة.')
@ABH.on(events.NewMessage(pattern=r'^تم$'))
async def start_game(event):
    chat_id = event.chat_id
    game = games.get(chat_id)
    if not game or not game["game_started"]:
        return
    if len(game["players"]) < 2:
        await event.respond('🔒 عدد اللاعبين غير كافٍ لبدء اللعبة.')
        reset_game(chat_id)
        return
    game["join_enabled"] = False
    await event.respond('✅ تم بدء اللعبة. الآن تفاعلوا بدون الرد على أي رسالة!')
@ABH.on(events.NewMessage(pattern=r'^اللاعبين$'))
async def show_players(event):
    chat_id = event.chat_id
    game = games.get(chat_id)
    if not game or not game["players"]:
        return
    mentions = []
    for uid in game["players"]:
        user = await ABH.get_entity(uid)
        mentions.append(f"[{user.first_name}](tg://user?id={uid})")
    await event.respond("👥 اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')
@ABH.on(events.NewMessage(incoming=True))
async def monitor_messages(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    game = games.get(chat_id)
    if not game or not game["game_started"] or game["join_enabled"]:
        return
    if sender_id in game["players"]:
        if chat_id not in active_players:
            active_players[chat_id] = set()
        active_players[chat_id].add(sender_id)
    if chat_id not in running_tasks:
        running_tasks.add(chat_id)
        asyncio.create_task(track_inactive_players(chat_id))
    reply = await event.get_reply_message()
    if sender_id in game["players"] and reply:
        now = datetime.utcnow()
        start_time = game["player_times"][sender_id]["start"]
        duration = now - start_time
        mention = f"[{(await ABH.get_entity(sender_id)).first_name}](tg://user?id={sender_id})"
        game["players"].remove(sender_id)
        game["player_times"].pop(sender_id, None)
        await event.reply(
            f'🚫 اللاعب {mention} رد على رسالة وخسر!\n⏱️ مدة اللعب: {format_duration(duration)}',
            parse_mode='md'
        )
        if len(game["players"]) == 1:
            await announce_winner(chat_id)
async def track_inactive_players(chat_id):
    while chat_id in games and games[chat_id]["game_started"]:
        await asyncio.sleep(60)
        game = games.get(chat_id)
        if not game:
            break
        current_players = game["players"].copy()
        current_active = active_players.get(chat_id, set())
        inactive_players = current_players - current_active
        for uid in inactive_players:
            game["players"].discard(uid)
            game["player_times"].pop(uid, None)
            user = await ABH.get_entity(uid)
            await ABH.send_message(
                chat_id,
                f'🚫 تم طرد اللاعب [{user.first_name}](tg://user?id={uid}) بسبب عدم التفاعل.',
                parse_mode='md'
            )
        active_players[chat_id] = set()
        if len(game["players"]) == 1:
            await announce_winner(chat_id)
            break
    running_tasks.discard(chat_id)
async def announce_winner(chat_id):
    game = games.get(chat_id)
    if not game or len(game["players"]) != 1:
        return
    winner_id = next(iter(game["players"]))
    winner = await ABH.get_entity(winner_id)
    win_time = datetime.utcnow() - game["player_times"][winner_id]["start"]
    await ABH.send_message(
        chat_id,
        f'🎉 انتهت اللعبة.\n🏆 الفائز هو: [{winner.first_name}](tg://user?id={winner_id})\n⏱️ مدة اللعب: {format_duration(win_time)}',
        parse_mode='md'
    )
    reset_game(chat_id)
ABH.run_until_disconnected()
