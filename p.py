from telethon import TelegramClient, events
from Resources import mention #type: ignore
import asyncio, os
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
games = {}
@ABH.on(events.NewMessage(pattern='/start'))
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
@ABH.on(events.NewMessage(pattern='/join'))
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
ABH.on(events.NewMessage(pattern='/players'))
async def players(event):
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

    players_list = "\n".join([f"• {mention(event, player)}" for player in games[chat_id]["players"]])
    await event.reply(f"👥 قائمة اللاعبين:\n{players_list}", parse_mode="md")
ABH.run_until_disconnected()
