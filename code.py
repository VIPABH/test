from ABH import ABH
from telethon import 
import json, os
FILE = "dialogs.json"
K_4X1 = 1910015590
def remove_user(user_id: int):
    if user_id in alert_ids:
        alert_ids.remove(user_id)
        save_alerts()
        print(f"تم حذف المستخدم {user_id} من القائمة.")
    else:
        print(f"المستخدم {user_id} غير موجود في القائمة.")
def load_alert():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return set(json.load(f))
    return set()
def save_alerts():
    with open(FILE, "w") as f:
        json.dump(list(alert_ids), f)
alert_ids = load_alert()
async def alert(message):
    try:
        await ABH.send_message(K_4X1, message)
    except:
        return
@ABH.on(events.NewMessage)
async def add_toalert(event):
    uid = None
    n = None
    if event.is_group:
        uid = event.chat_id
        n = event.chat.title or 'بدون اسم'
    elif event.is_private:
        uid = event.sender_id
        sender = await event.get_sender()
        n = await ment(sender)
    if uid not in alert_ids:
        alert_ids.add(uid)
        save_alerts()
        await hint(f'تم تسجيل محادثه جديده `{uid}` ↽ {n}')
@ABH.on(events.NewMessage(pattern="احصاء", from_users=[wfffp]))
async def showlenalert(event):
    await event.reply(str(len(alert_ids)))
x = 0
@ABH.on(events.NewMessage(pattern="/alert", from_users=[wfffp]))
async def set_alert(event):
    type = "نشر"
    await botuse(type)
    message_text = None
    media = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        message_text = replied_msg.text
        media = replied_msg.media
    else:
        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) > 1:
            message_text = command_parts[1]
        if event.media:
            media = event.media
    if not message_text and not media:
        await event.reply("يرجى الرد على رسالة تحتوي على ملف أو كتابة نص مع مرفق بعد `/alert`.")
        return
    await event.reply(f"🚀 جاري إرسال التنبيه إلى {len(alert_ids)} محادثة...")
    for dialog_id in alert_ids:
        try:
            if media:
                x += 1
                ء = await ABH.send_message(dialog_id, file=media, caption=message_text or "")
                await ء.delete()
            else:
                x += 1
                await ABH.send_message(dialog_id, f"{message_text}")
        except Exception as e:
            await alert(f"❌ فشل الإرسال إلى {dialog_id}: {e}")
            remove_user(dialog_id)
    await event.reply(f"{x} تم إرسال التنبيه لجميع المحادثات!")

# from telethon import events, Button
# from Resources import mention, ment
# import asyncio, uuid, random
# games = {}
# join_links = {}
# players = set()
# player_times = {}
# game_started = False
# join_enabled = False
# @ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
# async def injoin(event):
#     uid = event.pattern_match.group(1)
#     chat_id = join_links.get(uid)
#     print(chat_id)
#     if chat_id is None:
#         return await event.reply("هذا الزر غير صالح أو انتهت صلاحيته.")
#     if chat_id not in games:
#         return await event.reply("لا توجد لعبة نشطة في هذه المجموعة.")
#     s = await event.get_sender()
#     sm = await ment(s)
#     uid_str = str(s.id)
#     bot_username = (await ABH.get_me()).username
#     join_num = uid
#     print(games[chat_id]["players"])
#     print(uid_str)
#     if uid_str not in games[chat_id]["players"]:
#         return
#     await ABH.send_message(
#         chat_id,
#         f'المستخدم {sm} تم تسجيله في اللعبة والعدد صار ( {len(games[chat_id]["players"])} )',
#         buttons=[
#             [Button.url("انضم", url=f"https://t.me/{bot_username}?start={join_num}")]
#         ]
#     )
#     games[chat_id]["players"].add(uid_str)
#     await event.reply('تم تسجيلك')
# @ABH.on(events.NewMessage(pattern=r'^/(killAmorder|players)$'))
# async def unified_handler(event):
#     try:
#         chat_id = event.chat_id
#         sender = await event.get_sender()
#         command = event.raw_text.strip().lower()
#         if command == '/killamorder':
#             if chat_id in games:
#                 await event.reply("هناك لعبة جارية بالفعل.")
#                 return 
#             games[chat_id] = {
#                 "owner": sender.id,
#                 "players": set([str(sender.id)])
#             }
#             await start(event, chat_id)
#         elif command == 'players':
#             if chat_id not in games:
#                 return await event.reply("لم تبدأ أي لعبة بعد.")
#             await players(event)
#     except Exception as e:
#         print(e)
# async def start(event, chat_id):
#     sender = await event.get_sender()
#     m = await ment(sender)
#     join_num = str(uuid.uuid4())[:6]
#     join_links[join_num] = chat_id
#     bot_username = (await ABH.get_me()).username
#     uid = str(sender.id)
#     if uid not in games[chat_id]:
#         # games[chat_id]["players"].add(uid)
#         await ABH.send_message(
#         chat_id,
#         f"👋 أهلاً {m}\nتم بدء لعبة القاتل والمقتول.\nللانضمام اضغط 👇",
#         buttons=[
#             [Button.url("انضم", url=f"https://t.me/{bot_username}?start={join_num}")]])
# async def players(event):
#     chat_id = event.chat_id
#     if chat_id not in games:
#         await event.reply("لم تبدأ أي لعبة بعد.")
#         return
#     player_ids = games[chat_id]["players"]
#     if not player_ids:
#         await event.reply("لا يوجد لاعبين مسجلين حالياً.")
#         return 
#     mentions = []
#     for pid in player_ids:
#         user = await ABH.get_entity(int(pid))
#         mentions.append(f"[{user.first_name}](tg://user?id={pid})")
#     await event.reply("اللاعبون المسجلون:\n" + "\n".join(mentions), parse_mode='md')
# async def join(event, chat_id):
#     global games
#     sender = await event.get_sender()
#     ment = await ment(sender)
#     if chat_id not in games:
#         return await event.reply(" لم تبدأ أي لعبة في المجموعة بعد.")
#     if sender.id in games[chat_id]["players"]:
#         return await event.reply(f"{ment} أنت بالفعل مشارك في اللعبة.")
#     games[chat_id]["players"].add(sender.id)
#     await event.reply(f"تم انضمام {ment} إلى اللعبة في المجموعة.")
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
#     ment = await ment(killer)
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
#     killer_ment = await ment(killer)
#     target_ment = await ment(target)
#     await event.edit(f"🔫 {killer_ment} قتل ⇠ {target_ment}!")
#     if len(games[chat_id]["players"]) == 1:
#         winner_id = list(games[chat_id]["players"])[0]
#         games.pop(chat_id)
#         used_go.discard(chat_id)
#         winner = await ABH.get_entity(winner_id)
#         winner_ment = await ment(winner)
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
#     killer_ment = await ment(killer)
#     target_ment = await ment(target)
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
