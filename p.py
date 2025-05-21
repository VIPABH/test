from telethon import TelegramClient, events
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
async def kill(event):
    global games
    chat_id = event.chat_id
    sender = await event.get_sender()
    ment = await mention(event, sender)
    if chat_id not in games:
        await event.reply("❌ لم تبدأ أي لعبة بعد. أرسل /start أولاً.")
        return
    players = list(games[chat_id]["players"])
    if len(players) < 2:
        await event.reply("❌ لا يوجد لاعبون كافون للقتل.")
        return
    target_id = sender.id
    while target_id == sender.id:
        target_id = random.choice(players)
    target = await ABH.get_entity(target_id)
    target_mention = await mention(event, target)
    games[chat_id]["players"].remove(target_id)
    await event.reply(
        f"🔫 {ment} أطلق النار على {target_mention}!\n💀 تم إقصاؤه من اللعبة.",
        parse_mode="md"
    )
    if len(games[chat_id]["players"]) == 1:
        winner_id = list(games[chat_id]["players"])[0]
        winner = await ABH.get_entity(winner_id)
        winner_mention = await mention(event, winner)
        await event.reply(f"🏆 {winner_mention} هو الفائز! 🎉")
        del games[chat_id]
ABH.run_until_disconnected()
