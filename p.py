from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime, timedelta

# استيراد المتغيرات من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

players = set()
game_started = False
join_enabled = False
player_times = {}       # user_id: datetime
warned_players = set()  # user_ids الذين تم تنبيههم

# بدء اللعبة
@ABH.on(events.NewMessage(pattern=r'^/(vagueness|غموض)$'))
async def vagueness_start(event):
    global game_started, join_enabled, players, player_times, warned_players
    if game_started:
        await event.reply('اللعبة بالفعل بدأت.')
        return
    players.clear()
    player_times.clear()
    warned_players.clear()
    join_enabled = True
    game_started = True
    await event.reply('تم بدء لعبة الغموض، يسجل اللاعبون عبر أمر `انا`')

# تسجيل اللاعبين
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(event):
    user_id = event.sender_id
    if not game_started or not join_enabled:
        await event.reply('لم تبدأ اللعبة بعد.')
        return
    if user_id in players:
        await event.reply('أنت مسجل مسبقًا.')
        return
    players.add(user_id)
    player_times[user_id] = datetime.now()
    await event.reply('تم تسجيلك، انتظر بدء اللعبة.')

# عرض اللاعبين المسجلين
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

# بدء اللعبة ومراقبة غير النشطين
@ABH.on(events.NewMessage(pattern=r'^تم$'))
async def start_game(event):
    global join_enabled, warned_players
    if not game_started:
        await event.reply('لا توجد لعبة نشطة حالياً.')
        return

    join_enabled = False
    warned_players.clear()
    await event.respond('تم بدء اللعبة. الآن تفاعلوا بدون رد مباشر على الرسائل!')

    # مراقبة اللاعبين غير النشطين (دون استخدام create_task)
    while game_started and not join_enabled and len(players) > 1:
        now = datetime.now()
        for player_id in list(players):
            last_active = player_times.get(player_id)
            if not last_active:
                continue

            elapsed = now - last_active

            # تنبيه بعد 7 ثواني (قبل الطرد)
            if elapsed > timedelta(seconds=7) and player_id not in warned_players:
                warned_players.add(player_id)
                user = await ABH.get_entity(player_id)
                mention = f"[{user.first_name}](tg://user?id={player_id})"
                await ABH.send_message(event.chat_id, f"⚠️ {mention} لم تتفاعل منذ 7 ثواني، سيتم طردك بعد 3 ثواني إذا لم تتفاعل!", parse_mode='md')

            # طرد بعد 10 ثواني
            if elapsed > timedelta(seconds=10):
                players.remove(player_id)
                warned_players.discard(player_id)
                try:
                    user = await ABH.get_entity(player_id)
                    mention = f"[{user.first_name}](tg://user?id={player_id})"
                    await ABH.send_message(event.chat_id, f"🚫 تم إخراج {mention} من اللعبة بسبب عدم التفاعل.\n👥 عدد اللاعبين المتبقين: {len(players)}", parse_mode='md')
                except Exception as e:
                    print(f"❌ خطأ أثناء الطرد: {e}")

        if len(players) == 1:
            winner_id = next(iter(players))
            winner = await ABH.get_entity(winner_id)
            winner_mention = f"[{winner.first_name}](tg://user?id={winner_id})"
            duration = datetime.now() - player_times[winner_id]
            formatted_duration = str(timedelta(seconds=int(duration.total_seconds())))[2:7]
            await ABH.send_message(event.chat_id, f"🏁 انتهت اللعبة.\n🏆 الفائز هو: {winner_mention}\n🕒 مدة اللعب: {formatted_duration}", parse_mode='md')
            reset_game()
            break

        await asyncio.sleep(1)

# مراقبة الرسائل وردود اللاعبين
@ABH.on(events.NewMessage)
async def monitor_messages(event):
    global players, player_times, warned_players
    if not game_started or join_enabled:
        return

    sender_id = event.sender_id
    if event.text and event.text.startswith("/"):
        return

    if sender_id in players:
        now = datetime.now()
        player_times[sender_id] = now
        warned_players.discard(sender_id)  # إلغاء التنبيه إذا تفاعل اللاعب

        if await event.get_reply_message():
            players.remove(sender_id)
            duration = now - player_times.get(sender_id, now)
            formatted_duration = str(timedelta(seconds=int(duration.total_seconds())))[2:7]
            user = await event.client.get_entity(sender_id)
            mention = f"[{user.first_name}](tg://user?id={sender_id})"
            await event.reply(
                f'💥 اللاعب {mention} رد على رسالة وخسر!\n🕒 مدة اللعب: {formatted_duration}\n👥 عدد اللاعبين المتبقين: {len(players)}',
                parse_mode='md'
            )

            if len(players) == 1:
                winner_id = next(iter(players))
                winner = await event.client.get_entity(winner_id)
                winner_mention = f"[{winner.first_name}](tg://user?id={winner_id})"
                winner_duration = datetime.now() - player_times[winner_id]
                formatted_winner_duration = str(timedelta(seconds=int(winner_duration.total_seconds())))[2:7]
                await event.reply(
                    f'🏁 انتهت اللعبة.\n🏆 الفائز هو: {winner_mention}\n🕒 مدة اللعب: {formatted_winner_duration}',
                    parse_mode='md'
                )
                reset_game()

# إعادة تعيين اللعبة
def reset_game():
    global players, game_started, join_enabled, player_times, warned_players
    players.clear()
    player_times.clear()
    warned_players.clear()
    game_started = False
    join_enabled = False

# تشغيل البوت
ABH.run_until_disconnected()
