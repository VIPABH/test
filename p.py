from telethon import TelegramClient, events, Button
from Resources import mention #type: ignore
import asyncio, os, random
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
games = {}
async def start(event):
    global games
    if not event.is_group:
        await event.reply("❌ هذه اللعبة مخصصة للمجموعات فقط.")
        return
    chat_id = event.chat_id
    sender = await event.get_sender()
    ment = await mention(event, sender)
    if chat_id in games:
        await event.reply("⚠️ هنالك لعبة جارية بالفعل.\n⏳ انتظر حتى تنتهي اللعبة.")
    else:
        games[chat_id] = {
            "owner": sender.id,
            "players": set([sender.id])
        }
        await event.reply(
            f"👋 أهلاً {ment}\n✅ تم بدء لعبة القاتل والمقتول.\n🎮 أرسل /join للانضمام إلى اللعبة.",
            parse_mode="md"
        )
async def join(event):
    global games
    if not event.is_group:
        await event.reply("❌ هذه اللعبة مخصصة للمجموعات فقط.")
        return
    chat_id = event.chat_id
    sender = await event.get_sender()
    ment = await mention(event, sender)
    if chat_id not in games:
        await event.reply("❌ لم تبدأ أي لعبة بعد. أرسل /start لبدء اللعبة.")
        return
    if sender.id in games[chat_id]["players"]:
        await event.reply(f"✅ {ment} أنت بالفعل مشارك في اللعبة.", parse_mode="md")
        return
    games[chat_id]["players"].add(sender.id)
    await event.reply(f"✅ تم انضمام {ment} إلى اللعبة.", parse_mode="md")
async def players(event):
    global games
    if not event.is_group:
        await event.reply("❌ هذه اللعبة مخصصة للمجموعات فقط.")
        return
    chat_id = event.chat_id
    if chat_id not in games:
        await event.reply("❌ لم تبدأ أي لعبة بعد. أرسل /start لبدء اللعبة.")
        return
    player_ids = games[chat_id]["players"]
    players_list = []
    for user_id in player_ids:
        try:
            user = await ABH.get_entity(user_id)
            ment = await mention(event, user)
            players_list.append(f"• {ment}")
        except Exception:
            players_list.append(f"• مستخدم غير معروف (ID: {user_id})")
    players_text = "\n".join(players_list) if players_list else "لا يوجد لاعبين حالياً."
    await event.reply(f"👥 قائمة اللاعبين:\n{players_text}", parse_mode="md")
@ABH.on(events.NewMessage(pattern='/start|/join|/players'))
async def unified_handler(event):
    command = event.raw_text.split()[0].lower()
    if command == '/start':
        await start(event)
    elif command == '/join':
        await join(event)
    elif command == '/players':
        await players(event)
@ABH.on(events.NewMessage(pattern='/go'))
async def go(event):
    chat_id = event.chat_id
    if chat_id not in games or len(games[chat_id]["players"]) < 2:
        return await event.reply("❌ تحتاج على الأقل لاعبين اثنين.")
    await assign_killer(chat_id)
async def assign_killer(chat_id):
    players = list(games[chat_id]["players"])
    killer_id = random.choice(players)
    games[chat_id]["killer"] = killer_id
    killer = await ABH.get_entity(killer_id)
    ment = await mention(None, killer)
    await ABH.send_message(
        chat_id,
        f"🔫 القاتل هو {ment}! اضغط الزر التالي لاختيار ضحية.",
        buttons=[Button.inline("🔪 اقتل الآن", data=b"kill")],
    )
@ABH.on(events.CallbackQuery(data=b"kill"))
async def handle_kill(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    if chat_id not in games or sender_id != games[chat_id]["killer"]:
        return await event.answer("❌ هذا الزر ليس لك.", alert=True)
    players = list(games[chat_id]["players"])
    if len(players) <= 2:
        winner = [p for p in players if p != sender_id][0]
        games.pop(chat_id)
        win_entity = await ABH.get_entity(winner)
        win_ment = await mention(None, win_entity)
        return await event.edit(f"🏆 الفائز هو {win_ment}!")
    target_id = sender_id
    while target_id == sender_id:
        target_id = random.choice(players)
    games[chat_id]["players"].remove(target_id)
    target = await ABH.get_entity(target_id)
    killer = await ABH.get_entity(sender_id)
    killer_ment = await mention(None, killer)
    target_ment = await mention(None, target)
    await event.edit(f"💥 {killer_ment} قتل {target_ment}!")
    await asyncio.sleep(5)
    await assign_killer(chat_id)
ABH.run_until_disconnected()
