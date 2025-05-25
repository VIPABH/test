from telethon import TelegramClient, events
from datetime import datetime
import os, asyncio
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تشغيل البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# متغيرات التحكم باللعبة
players = set()
game_started = False
join_enabled = False

# بدء اللعبة
@ABH.on(events.NewMessage(pattern=r'^/(vagueness|غموض)$'))
async def vagueness_start(event):
    global game_started, join_enabled, players
    if game_started:
        await event.reply('اللعبة بالفعل بدأت.')
        return
    players.clear()
    join_enabled = True
    game_started = True
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
    await event.reply('تم تسجيلك، انتظر بدء اللعبة.')

# إنهاء التسجيل وبدء التحدي
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
@ABH.on(events.NewMessage(pattern=r'^اللاعبين$'))
async def show_players(event):
    if not players:
        await event.reply("لا يوجد لاعبون مسجلون حالياً.")
        return
    mentions = []
    for user_id in players:
        user = await ABH.get_entity(user_id)
        mentions.append(f"[{user.first_name}](tg://user?id={user_id})")
    await event.reply("اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')

def format_duration(duration):
    total_seconds = int(duration.total_seconds())
    if total_seconds < 3600:  # أقل من ساعة
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    else:  # أكثر من ساعة
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

@ABH.on(events.NewMessage)
async def monitor_messages(event):
    global players
    if not game_started or join_enabled:
        return

    sender_id = event.sender_id
    reply = await event.get_reply_message()

    if sender_id in players and reply:
        now = datetime.now()
        player_times[sender_id]["end"] = now
        duration = now - player_times[sender_id]["start"]
        formatted_duration = format_duration(duration)

        user = await event.client.get_entity(sender_id)
        mention = f"[{user.first_name}](tg://user?id={sender_id})"
        players.remove(sender_id)
        await event.reply(
            f'اللاعب {mention} رد على رسالة وخسر!\nمدة اللعب: {formatted_duration}',
            parse_mode='md'
        )

        if len(players) == 1:
            winner_id = next(iter(players))
            winner = await event.client.get_entity(winner_id)
            winner_mention = f"[{winner.first_name}](tg://user?id={winner_id})"
            winner_duration = datetime.now() - player_times[winner_id]["start"]
            formatted_winner_duration = format_duration(winner_duration)

            await event.reply(
                f'انتهت اللعبة.\nالفائز هو: {winner_mention}\nمدة اللعب: {formatted_winner_duration}',
                parse_mode='md'
            )
            reset_game()
# دالة لإعادة تعيين اللعبة
def reset_game():
    global players, game_started, join_enabled
    players.clear()
    game_started = False
    join_enabled = False

# تشغيل البوت
ABH.run_until_disconnected()
