from telethon import TelegramClient, events, Button
from datetime import datetime, timedelta
from Resources import mention
import os, asyncio, uuid, random
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
async def run_cmd(command: str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode
@ABH.on(events.NewMessage(pattern="^تحديث$"))
async def update_repo(event):
    msg = await event.edit(" جاري جلب آخر التحديثات من الريبو عبر...")
    stdout, stderr, code = await run_cmd("git pull")
    if code == 0:
        await msg.edit(f" تحديث السورس بنجاح")
    else:
        await msg.edit(f" حدث خطأ أثناء التحديث:\n\n{stderr}")
games = {}
join_links = {}

# دالة مساعدة لعمل منشن للاعب
async def mention(event, user):
    return f"[{user.first_name}](tg://user?id={user.id})"

players = set()
game_started = False
join_enabled = False

# # بدء اللعبة
players = set()
player_times = {}
game_started = False
join_enabled = False

# دالة تنسيق مدة اللعب
def format_duration(duration: timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes} دقيقة و {seconds} ثانية"

# دالة لإعادة تعيين اللعبة
def reset_game():
    global players, game_started, join_enabled, player_times
    players.clear()
    player_times.clear()
    game_started = False
    join_enabled = False

# بدء اللعبة
@ABH.on(events.NewMessage(pattern=r'^/(vagueness|غموض)$'))
async def vagueness_start(event):
    global game_started, join_enabled, players
    if game_started:
        await event.respond('⚠️ اللعبة بالفعل بدأت.')
        return
    players.clear()
    join_enabled = True
    game_started = True
    await event.respond('🎮 تم بدء لعبة الغموض، يسجل اللاعبون عبر أمر `انا`')

# تسجيل اللاعبين
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(event):
    global join_enabled
    user_id = event.sender_id
    if not game_started or not join_enabled:
        await event.respond('❗ لم تبدأ اللعبة بعد.')
        return
    if user_id in players:
        await event.respond('✅ أنت مسجل مسبقًا.')
        return
    players.add(user_id)
    player_times[user_id] = {"start": datetime.utcnow()}
    await event.respond('📝 تم تسجيلك، انتظر بدء اللعبة.')

# إنهاء التسجيل وبدء التحدي
@ABH.on(events.NewMessage(pattern=r'^تم$'))
async def start_game(event):
    global join_enabled
    if not game_started:
        await event.respond('🚫 لا توجد لعبة نشطة حالياً.')
        return
    if len(players) < 2:
        await event.respond('🔒 عدد اللاعبين غير كافٍ لبدء اللعبة.')
        reset_game()
        return
    join_enabled = False
    await event.respond('✅ تم بدء اللعبة. الآن تفاعلوا بدون الرد على أي رسالة!')

# عرض اللاعبين المسجلين
@ABH.on(events.NewMessage(pattern=r'^اللاعبين$'))
async def show_players(event):
    if not players:
        await event.respond("لا يوجد لاعبون مسجلون حالياً.")
        return
    mentions = []
    for user_id in players:
        user = await ABH.get_entity(user_id)
        mentions.append(f"[{user.first_name}](tg://user?id={user_id})")
    await event.respond("👥 اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')

# مراقبة الردود من اللاعبين
@ABH.on(events.NewMessage(incoming=True))
async def monitor_messages(event):
    global players, player_times, game_started, join_enabled

    if not game_started or join_enabled:
        return

    sender_id = event.sender_id
    reply = await event.get_reply_message()

    if sender_id in players and reply and sender_id in player_times:
        now = datetime.utcnow()
        player_times[sender_id]["end"] = now
        duration = now - player_times[sender_id]["start"]
        formatted_duration = format_duration(duration)
        user = await event.client.get_entity(sender_id)
        mention = f"[{user.first_name}](tg://user?id={sender_id})"
        players.remove(sender_id)

        await event.reply(
            f'🚫 اللاعب {mention} رد على رسالة وخسر!\n⏱️ مدة اللعب: {formatted_duration}',
            parse_mode='md'
        )

        if len(players) == 1:
            winner_id = next(iter(players))
            winner = await event.client.get_entity(winner_id)
            winner_mention = f"[{winner.first_name}](tg://user?id={winner_id})"
            winner_duration = datetime.utcnow() - player_times[winner_id]["start"]
            formatted_winner_duration = format_duration(winner_duration)

            await event.reply(
                f'🎉 انتهت اللعبة.\n🏆 الفائز هو: {winner_mention}\n⏱️ مدة اللعب: {formatted_winner_duration}',
                parse_mode='md'
            )
            reset_game()
def reset_game():
    global players, game_started, join_enabled
    players.clear()
    game_started = False
    join_enabled = False

# @ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
# async def injoin(event):
#     uid = event.pattern_match.group(1)
#     chat_id = join_links.get(uid)
#     if chat_id is None:
#         return await event.reply("هذا الزر غير صالح أو انتهت صلاحيته.")
    
#     if chat_id not in games:
#         return await event.reply("لا توجد لعبة نشطة في هذه المجموعة.")
    
#     s = await event.get_sender()
#     sm = await mention(event, s)
#     uid_str = str(s.id)

#     if event.is_group and uid_str not in games[chat_id]["players"]:
#         games[chat_id]["players"].add(uid_str)
#         bot_username = (await ABH.get_me()).username
#         join_num = uid  # نستخدم نفس الكود في الرابط
        
#         await ABH.send_message(
#             chat_id,
#             f'المستخدم {sm} تم تسجيله في اللعبة والعدد صار ( {len(games[chat_id]["players"])} )',
#             buttons=[
#                 [Button.url("انضم", url=f"https://t.me/{bot_username}?start={join_num}")]
#             ]
#         )
#         await event.reply("تم تسجيلك في اللعبة.")

# # أمر بدء اللعبة
# @ABH.on(events.NewMessage(pattern=r'^/(killAmorder|players)$'))
# async def unified_handler(event):
#     chat_id = event.chat_id
#     sender = await event.get_sender()
#     command = event.raw_text.strip().lower()
    
#     if command == '/killamorder':
#         if chat_id in games:
#             return await event.reply("هناك لعبة جارية بالفعل.")
#         games[chat_id] = {
#             "owner": sender.id,
#             "players": set([str(sender.id)])
#         }
#         await start(event, chat_id)
        
#     elif command == 'players':
#         if chat_id not in games:
#             return await event.reply("لم تبدأ أي لعبة بعد.")
#         await players(event)

# # دالة بدء اللعبة - ترسل رسالة مع زر انضمام
# async def start(event, chat_id):
#     sender = await event.get_sender()
#     ment = await mention(event, sender)
#     join_num = str(uuid.uuid4())[:6]
#     join_links[join_num] = chat_id
#     bot_username = (await ABH.get_me()).username
#     uid = str(sender.id)
    
#     if event.is_group and uid not in games[chat_id]["players"]:
#         games[chat_id]["players"].add(uid)
    
#     await ABH.send_message(
#         chat_id,
#         f"👋 أهلاً {ment}\nتم بدء لعبة القاتل والمقتول.\nللانضمام اضغط 👇",
#         buttons=[
#             [Button.url("انضم", url=f"https://t.me/{bot_username}?start={join_num}")]
#         ]
#     )

# # دالة عرض اللاعبين
# async def players(event):
#     chat_id = event.chat_id
#     if chat_id not in games:
#         return await event.reply("لم تبدأ أي لعبة بعد.")
    
#     player_ids = games[chat_id]["players"]
#     if not player_ids:
#         return await event.reply("لا يوجد لاعبين مسجلين حالياً.")
    
#     mentions = []
#     for pid in player_ids:
#         user = await ABH.get_entity(int(pid))
#         mentions.append(f"[{user.first_name}](tg://user?id={pid})")
    
#     await event.reply("اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')
# async def join(event, chat_id):
#     global games
#     sender = await event.get_sender()
#     ment = await mention(event, sender)
#     if chat_id not in games:
#         return await event.reply(" لم تبدأ أي لعبة في المجموعة بعد.")
#     if sender.id in games[chat_id]["players"]:
#         return await event.reply(f"{ment} أنت بالفعل مشارك في اللعبة.")
#     games[chat_id]["players"].add(sender.id)
#     await event.reply(f"تم انضمام {ment} إلى اللعبة في المجموعة.")
# async def players(event):
#     global games
#     if not event.is_group:
#         return
#     chat_id = event.chat_id
#     if chat_id not in games:
#         return
#     player_ids = games[chat_id]["players"]
#     players_list = []
#     for user_id in player_ids:
#         try:
#             user = await ABH.get_entity(user_id)
#             ment = await mention(event, user)
#             players_list.append(f"• {ment}")
#         except Exception:
#             players_list.append(f"• مستخدم غير معروف (ID: {user_id})")
#     players_text = "\n".join(players_list) if players_list else "لا يوجد لاعبين حالياً."
#     await event.reply(f"👥 قائمة اللاعبين:\n{players_text}", parse_mode="md")
# used_go = set()
# @ABH.on(events.NewMessage(pattern='^تم$'))
# async def go(event):
#     chat_id = event.chat_id
#     if chat_id not in games or len(games[chat_id]["players"]) < 2:
#         return await event.reply(" تحتاج على الأقل لاعبين اثنين.")
#     if chat_id in used_go:
#         return await event.reply(" تم بالفعل بدء جولة القتل. انتظر حتى تنتهي.")
#     used_go.add(chat_id)
#     await assign_killer(chat_id)
# async def assign_killer(chat_id):
#     players = list(games[chat_id]["players"])
#     killer_id = random.choice(players)
#     games[chat_id]["killer"] = killer_id

#     killer = await ABH.get_entity(killer_id)
#     ment = await mention(None, killer)
#     await ABH.send_message(
#         chat_id,
#         f"🔫 القاتل هو {ment}! لديك 30 ثانية لقتل أحدهم.\nاختر أحد الخيارين:",
#         buttons=[
#             [Button.inline("🔪 قتل عشوائي", data=b"kill")],
#             [Button.inline("🎯 اختيار ضحية", data=b"select")]
#         ]
#     )
#     async def killer_timeout():
#         await asyncio.sleep(30)
#         if chat_id in games and games[chat_id].get("killer") == killer_id:
#             await ABH.send_message(chat_id, " انتهى الوقت! سيتم تعيين قاتل جديد.")
#             await asyncio.sleep(3)
#             await assign_killer(chat_id)
#     asyncio.create_task(killer_timeout())
# @ABH.on(events.CallbackQuery(data=b"kill"))
# async def handle_kill(event):
#     chat_id = event.chat_id
#     sender_id = event.sender_id
#     if chat_id not in games or sender_id != games[chat_id].get("killer"):
#         return await event.answer(" هذا الزر ليس لك.", alert=True)
#     players = list(games[chat_id]["players"])
#     if len(players) <= 1:
#         return
#     target_id = sender_id
#     while target_id == sender_id:
#         target_id = random.choice(players)
#     games[chat_id]["players"].remove(target_id)
#     target = await ABH.get_entity(target_id)
#     killer = await ABH.get_entity(sender_id)
#     killer_ment = await mention(None, killer)
#     target_ment = await mention(None, target)
#     await event.edit(f"🔫 {killer_ment} قتل ⇠ {target_ment}!")
#     if len(games[chat_id]["players"]) == 1:
#         winner_id = list(games[chat_id]["players"])[0]
#         games.pop(chat_id)
#         used_go.discard(chat_id)
#         winner = await ABH.get_entity(winner_id)
#         winner_ment = await mention(None, winner)
#         await ABH.send_message(chat_id, f"🏆 {winner_ment} هو الفائز الأخير! 🎉")
#         return
#     await asyncio.sleep(5)
#     await assign_killer(chat_id)
# @ABH.on(events.CallbackQuery(data=b"select"))
# async def handle_select(event):
#     chat_id = event.chat_id
#     sender_id = event.sender_id
#     if chat_id not in games or sender_id != games[chat_id].get("killer"):
#         return await event.answer(" هذا الزر ليس لك.", alert=True)
#     players = list(games[chat_id]["players"])
#     players.remove(sender_id)
#     buttons = [
#         Button.inline(
#             f"🔪 قتل {(await ABH.get_entity(player)).first_name}",
#             data=f"kill_{player}".encode()
#         ) for player in players
#     ]
#     button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
#     await event.edit(" اختر الضحية:", buttons=button_rows)
# @ABH.on(events.CallbackQuery(pattern=b"kill_"))
# async def handle_select_kill(event):
#     chat_id = event.chat_id
#     sender_id = event.sender_id
#     if chat_id not in games or sender_id != games[chat_id].get("killer"):
#         return await event.answer(" هذا الزر ليس لك.", alert=True)
#     data = event.data.decode()
#     target_id = int(data.split("_")[1])
#     if target_id not in games[chat_id]["players"]:
#         return await event.answer(" هذا اللاعب غير موجود.", alert=True)
#     games[chat_id]["players"].remove(target_id)
#     target = await ABH.get_entity(target_id)
#     killer = await ABH.get_entity(sender_id)
#     killer_ment = await mention(None, killer)
#     target_ment = await mention(None, target)
#     await event.edit(f"🗡️ {killer_ment} اختار وقتل ↤ {target_ment}!")
#     if len(games[chat_id]["players"]) == 1:
#         winner_id = list(games[chat_id]["players"])[0]
#         games.pop(chat_id)
#         used_go.discard(chat_id)
#         winner = await ABH.get_entity(winner_id)
#         winner_ment = await mention(None, winner)
#         await ABH.send_message(chat_id, f"🏆 {winner_ment} هو الفائز الأخير! 🎉")
#         return
#     await asyncio.sleep(5)
#     await assign_killer(chat_id)

# تشغيل البوت
ABH.run_until_disconnected()
