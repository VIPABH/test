from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime, timedelta

# استيراد المتغيرات من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# متغيرات اللعبة
players = set()
player_times = {}  # user_id: {"start": datetime, "end": datetime}
game_started = False
join_enabled = False
game_chat_id = None  # معرف المجموعة التي تجري فيها اللعبة

# بدء اللعبة
@ABH.on(events.NewMessage(pattern=r'^/(vagueness|غموض)$'))
async def vagueness_start(event):
    global game_started, join_enabled, players, player_times, game_chat_id
    if game_started:
        await event.reply('اللعبة بالفعل بدأت.')
        return
    players.clear()
    player_times.clear()
    join_enabled = True
    game_started = True
    game_chat_id = event.chat_id  # حفظ معرف المجموعة
    asyncio.create_task(kick_inactive_players())  # بدء فحص التفاعل
    await event.reply('تم بدء لعبة الغموض، يسجل اللاعبون عبر أمر `انا`')

# تسجيل اللاعبين
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(event):
    global join_enabled
    user_id = event.sender_id
    if not game_started or not join_enabled:
        await event.reply('لم تبدأ اللعبة بعد.')
        return
    if user_id in players:
        await event.reply('أنت مسجل مسبقًا.')
        return
    players.add(user_id)
    player_times[user_id] = {"start": datetime.now(), "end": None}
    await event.reply('تم تسجيلك، انتظر بدء اللعبة.')

# عرض اللاعبين
@ABH.on(events.NewMessage(pattern=r'^!الاعبين$'))
async def show_players(event):
    if not players:
        await event.reply("لا يوجد لاعبون مسجلون حالياً.")
        return
    mentions = []
    for user_id in players:
        user = await ABH.get_entity(user_id)
        mentions.append(f"[{user.first_name}](tg://user?id={user_id})")
    await event.reply("اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')

# بدء اللعبة بعد إغلاق التسجيل
@ABH.on(events.NewMessage(pattern=r'^تم$'))
async def start_game(event):
    global join_enabled
    if not game_started:
        await event.reply('لا توجد لعبة نشطة حالياً.')
        return
    if len(players) < 2:
        await event.reply('عدد اللاعبين غير كافٍ لبدء اللعبة.')
        reset_game()
        return
    join_enabled = False
    await event.respond('تم بدء اللعبة. الآن تفاعلوا بدون رد مباشر على الرسائل!')

# مراقبة الرسائل
@ABH.on(events.NewMessage)
async def monitor_messages(event):
    global players, player_times
    if not game_started or join_enabled:
        return

    sender_id = event.sender_id
    if sender_id in players:
        now = datetime.now()
        player_times[sender_id]["start"] = now

        if await event.get_reply_message():
            players.remove(sender_id)
            duration = now - player_times[sender_id]["start"]
            formatted_duration = str(timedelta(seconds=int(duration.total_seconds())))[2:7]
            user = await event.client.get_entity(sender_id)
            mention = f"[{user.first_name}](tg://user?id={sender_id})"

            await event.reply(
                f'اللاعب {mention} رد على رسالة وخسر!\nمدة اللعب: {formatted_duration}',
                parse_mode='md'
            )

            if len(players) == 1:
                winner_id = next(iter(players))
                winner = await event.client.get_entity(winner_id)
                winner_mention = f"[{winner.first_name}](tg://user?id={winner_id})"
                winner_duration = datetime.now() - player_times[winner_id]["start"]
                formatted_winner_duration = str(timedelta(seconds=int(winner_duration.total_seconds())))[2:7]
                await event.reply(
                    f'انتهت اللعبة.\nالفائز هو: {winner_mention}\nمدة اللعب: {formatted_winner_duration}',
                    parse_mode='md'
                )
                reset_game()

# فحص غير المتفاعلين كل 5 دقائق وطردهم
async def kick_inactive_players():
    global game_chat_id
    while game_started and not join_enabled:
        now = datetime.now()
        to_remove = []
        for player_id in list(players):
            last_active = player_times.get(player_id, {}).get("start")
            if last_active and now - last_active > timedelta(minutes=5):
                to_remove.append(player_id)

        for player_id in to_remove:
            players.remove(player_id)
            try:
                await ABH.kick_participant(game_chat_id, player_id)
                user = await ABH.get_entity(player_id)
                mention = f"[{user.first_name}](tg://user?id={player_id})"
                await ABH.send_message(game_chat_id, f"تم طرد {mention} بسبب عدم التفاعل.", parse_mode='md')
            except Exception as e:
                print(f"خطأ أثناء الطرد: {e}")
        await asyncio.sleep(10)  # كل 5 دقائق

# إعادة تعيين اللعبة
def reset_game():
    global players, game_started, join_enabled, player_times, game_chat_id
    players.clear()
    player_times.clear()
    game_started = False
    join_enabled = False
    game_chat_id = None

# تشغيل البوت
ABH.run_until_disconnected()
