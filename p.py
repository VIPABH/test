from telethon import TelegramClient, events, Button
from datetime import datetime, timedelta
from Resources import mention
import os, asyncio, uuid, random
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
import asyncio
from datetime import datetime, timedelta
from telethon import events

games = {}
active_players = {}

def format_duration(duration: timedelta) -> str:
    minutes, seconds = divmod(int(duration.total_seconds()), 60)
    return f"{minutes} دقيقة و {seconds} ثانية"

def reset_game(chat_id):
    if chat_id in games:
        del games[chat_id]
    if chat_id in active_players:
        del active_players[chat_id]
@ABH.on(events.NewMessage(pattern=r'^/(vagueness)$|^غموض$'))
# @ABH.on(events.NewMessage(pattern=r'^/vagueness|غموض$'))
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
    # بدء مهمة دورية لطرد غير النشطين

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
    # if len(game["players"]) < 2:
    #     await event.respond('🔒 عدد اللاعبين غير كافٍ لبدء اللعبة.')
    #     reset_game(chat_id)
    #     return
    game["join_enabled"] = False
    await event.respond('✅ تم بدء اللعبة. الآن تفاعلوا بدون الرد على أي رسالة!')
    asyncio.create_task(track_inactive_players(chat_id))

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

    if chat_id not in active_players:
        active_players[chat_id] = set()
    active_players[chat_id].add(sender_id)
    reply = await event.get_reply_message()
    asyncio.create_task(track_inactive_players(chat_id))
    if sender_id in game["players"] and reply and sender_id in game["player_times"]:
        now = datetime.utcnow()
        game["player_times"][sender_id]["end"] = now
        duration = now - game["player_times"][sender_id]["start"]
        mention = f"[{(await ABH.get_entity(sender_id)).first_name}](tg://user?id={sender_id})"
        game["players"].remove(sender_id)
        await event.reply(
            f'🚫 اللاعب {mention} رد على رسالة وخسر!\n⏱️ مدة اللعب: {format_duration(duration)}',
            parse_mode='md'
        )
    if len(game["players"]) == 1:
        winner_id = next(iter(game["players"]))
        winner = await ABH.get_entity(winner_id)
        win_time = datetime.utcnow() - game["player_times"][winner_id]["start"]
        await event.reply(
            f'🎉 انتهت اللعبة.\n🏆 الفائز هو: [{winner.first_name}](tg://user?id={winner_id})\n⏱️ مدة اللعب: {format_duration(win_time)}',
            parse_mode='md'
        )
        reset_game(chat_id)
async def track_inactive_players(chat_id):
    while chat_id in games and games[chat_id]["game_started"]:
        await asyncio.sleep(3)  # 5 دقائق

        game = games.get(chat_id)
        if not game:
            break

        # جلب اللاعبين المسجلين
        registered_players = game["players"].copy()
        # جلب المتفاعلين خلال الـ5 دقائق الماضية
        active_now = active_players.get(chat_id, set())

        # تحديد من لم يتفاعل أبدًا خلال الفترة
        inactive = registered_players - active_now

        for uid in inactive:
            game["players"].discard(uid)
            game["player_times"].pop(uid, None)
            try:
                user = await ABH.get_entity(uid)
                mention = f"[{user.first_name}](tg://user?id={uid})"
            except:
                mention = f"مستخدم {uid}"
            await ABH.send_message(
                chat_id,
                f'🚫 تم طرد اللاعب {mention} بسبب عدم التفاعل خلال 5 دقائق.',
                parse_mode='md'
            )

        # إعادة تعيين المتفاعلين للدورة القادمة
        active_players[chat_id] = set()

ABH.run_until_disconnected()
