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

    # إرسال رسالة فيها الزرين: القتل العشوائي + الاختياري
    await ABH.send_message(
        chat_id,
        f"🔫 القاتل هو {ment}! لديك 30 ثانية لقتل أحدهم.\nاختر أحد الخيارين:",
        buttons=[
            [Button.inline("🔪 قتل عشوائي", data=b"kill")],
            [Button.inline("🎯 اختيار ضحية", data=b"select")]
        ]
    )

    # بدء مؤقت 30 ثانية. إذا لم يُقتل أحد، يُعاد تعيين قاتل.
    async def killer_timeout():
        await asyncio.sleep(30)
        if chat_id in games and games[chat_id].get("killer") == killer_id:
            await ABH.send_message(chat_id, "⌛ انتهى الوقت! سيتم تعيين قاتل جديد.")
            await assign_killer(chat_id)

    asyncio.create_task(killer_timeout())

# قتل عشوائي
@ABH.on(events.CallbackQuery(data=b"kill"))
async def handle_kill(event):
    chat_id = event.chat_id
    sender_id = event.sender_id

    if chat_id not in games or sender_id != games[chat_id].get("killer"):
        return await event.answer("❌ هذا الزر ليس لك.", alert=True)

    players = list(games[chat_id]["players"])
    if len(players) <= 1:
        return

    # اختيار ضحية غير القاتل
    target_id = sender_id
    while target_id == sender_id:
        target_id = random.choice(players)

    games[chat_id]["players"].remove(target_id)
    target = await ABH.get_entity(target_id)
    killer = await ABH.get_entity(sender_id)
    killer_ment = await mention(None, killer)
    target_ment = await mention(None, target)

    await event.edit(f"🔫 {killer_ment} قتل {target_ment}!")

    # فحص الفوز
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

# عرض الأسماء لاختيار الضحية يدويًا
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
