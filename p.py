from telethon import TelegramClient, events, Button
from Resources import mention #type: ignore
import asyncio, os, random, uuid
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
games = {}
join_links = {}
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def injoin(event):
    uid = event.pattern_match.group(1)
    chat_id = join_links.get(uid)
    if chat_id is None:
        return await event.reply("❌ هذا الرابط غير صالح أو انتهت صلاحيته.")
    await join(event, chat_id)
@ABH.on(events.NewMessage(pattern=r'^/(killAmorder|players)$'))
async def unified_handler(event):
    global games
    chat_id = event.chat_id
    sender = await event.get_sender()
    command = event.raw_text.strip().lower()
    if command == '/killamorder':
        if chat_id in games:
            return await event.reply("⚠️ هناك لعبة جارية بالفعل.")
        games[chat_id] = {
            "owner": sender.id,
            "players": set([sender.id])
        }
        return await start(event, chat_id)    
    elif command == '/players':
        if chat_id not in games:
            return await event.reply("❌ لم تبدأ أي لعبة بعد.")
        return await players(event)
async def start(event, chat_id):
    global games, join_links
    sender = await event.get_sender()
    ment = await mention(event, sender)
    join_num = str(uuid.uuid4())[:6]
    join_links[join_num] = chat_id
    bot_username = (await ABH.get_me()).username
    await event.reply(
        f"👋 أهلاً {ment}\nتم بدء لعبة القاتل والمقتول.\nللانضمام اضغط 👇",
        buttons=[
            [Button.url("انضم", url=f"https://t.me/{bot_username}?start={join_num}")],
            [Button.inline("قائمة اللاعبين", b"players")]
        ]
    )
async def join(event, chat_id):
    global games
    sender = await event.get_sender()
    ment = await mention(event, sender)
    if chat_id not in games:
        return await event.reply("❌ لم تبدأ أي لعبة في المجموعة بعد.")
    if sender.id in games[chat_id]["players"]:
        return await event.reply(f"{ment} أنت بالفعل مشارك في اللعبة.")
    games[chat_id]["players"].add(sender.id)
    await event.reply(f"✅ تم انضمام {ment} إلى اللعبة في المجموعة.")
async def players(event):
    global games
    if not event.is_group:
        return
    chat_id = event.chat_id
    if chat_id not in games:
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
used_go = set()
@ABH.on(events.NewMessage(pattern='/go'))
async def go(event):
    chat_id = event.chat_id
    if chat_id not in games or len(games[chat_id]["players"]) < 2:
        return await event.reply("❌ تحتاج على الأقل لاعبين اثنين.")
    if chat_id in used_go:
        return await event.reply("⛔ تم بالفعل بدء جولة القتل. انتظر حتى تنتهي.")
    used_go.add(chat_id)
    await assign_killer(chat_id)
async def assign_killer(chat_id):
    players = list(games[chat_id]["players"])
    killer_id = random.choice(players)
    games[chat_id]["killer"] = killer_id

    killer = await ABH.get_entity(killer_id)
    ment = await mention(None, killer)
    await ABH.send_message(
        chat_id,
        f"🔫 القاتل هو {ment}! لديك 30 ثانية لقتل أحدهم.\nاختر أحد الخيارين:",
        buttons=[
            [Button.inline("🔪 قتل عشوائي", data=b"kill")],
            [Button.inline("🎯 اختيار ضحية", data=b"select")]
        ]
    )
    async def killer_timeout():
        await asyncio.sleep(30)
        if chat_id in games and games[chat_id].get("killer") == killer_id:
            await ABH.send_message(chat_id, "⌛ انتهى الوقت! سيتم تعيين قاتل جديد.")
            await assign_killer(chat_id)
    asyncio.create_task(killer_timeout())
@ABH.on(events.CallbackQuery(data=b"kill"))
async def handle_kill(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    if chat_id not in games or sender_id != games[chat_id].get("killer"):
        return await event.answer("❌ هذا الزر ليس لك.", alert=True)
    players = list(games[chat_id]["players"])
    if len(players) <= 1:
        return
    target_id = sender_id
    while target_id == sender_id:
        target_id = random.choice(players)
    games[chat_id]["players"].remove(target_id)
    target = await ABH.get_entity(target_id)
    killer = await ABH.get_entity(sender_id)
    killer_ment = await mention(None, killer)
    target_ment = await mention(None, target)
    await event.edit(f"🔫 {killer_ment} قتل {target_ment}!")
    if len(games[chat_id]["players"]) == 1:
        winner_id = list(games[chat_id]["players"])[0]
        games.pop(chat_id)
        used_go.discard(chat_id)
        winner = await ABH.get_entity(winner_id)
        winner_ment = await mention(None, winner)
        await ABH.send_message(chat_id, f"🏆 {winner_ment} هو الفائز الأخير! 🎉")
        return
    await asyncio.sleep(5)
    await assign_killer(chat_id)
@ABH.on(events.CallbackQuery(data=b"select"))
async def handle_select(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    if chat_id not in games or sender_id != games[chat_id].get("killer"):
        return await event.answer("❌ هذا الزر ليس لك.", alert=True)
    players = list(games[chat_id]["players"])
    players.remove(sender_id)
    buttons = [
        Button.inline(
            f"🔪 قتل {(await ABH.get_entity(player)).first_name}",
            data=f"kill_{player}".encode()
        ) for player in players
    ]
    button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await event.edit("🎯 اختر الضحية:", buttons=button_rows)
@ABH.on(events.CallbackQuery(pattern=b"kill_"))
async def handle_select_kill(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    if chat_id not in games or sender_id != games[chat_id].get("killer"):
        return await event.answer("❌ هذا الزر ليس لك.", alert=True)
    data = event.data.decode()
    target_id = int(data.split("_")[1])
    if target_id not in games[chat_id]["players"]:
        return await event.answer("❌ هذا اللاعب غير موجود.", alert=True)
    games[chat_id]["players"].remove(target_id)
    target = await ABH.get_entity(target_id)
    killer = await ABH.get_entity(sender_id)
    killer_ment = await mention(None, killer)
    target_ment = await mention(None, target)
    await event.edit(f"🗡️ {killer_ment} اختار وقتل ↤ {target_ment}!")
    if len(games[chat_id]["players"]) == 1:
        winner_id = list(games[chat_id]["players"])[0]
        games.pop(chat_id)
        used_go.discard(chat_id)
        winner = await ABH.get_entity(winner_id)
        winner_ment = await mention(None, winner)
        await ABH.send_message(chat_id, f"🏆 {winner_ment} هو الفائز الأخير! 🎉")
        return
    await asyncio.sleep(5)
    await assign_killer(chat_id)
ABH.run_until_disconnected()
