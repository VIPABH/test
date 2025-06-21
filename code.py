from Resources import football, questions, mention, ment, wfffp #type: ignore
from top import points, add_points #type: ignore
from datetime import datetime, timedelta
import random, asyncio, time, os, json
from telethon import Button, events
from ABH import ABH #type: ignore
from other import botuse
from faker import Faker
USER_DATA_FILE = "trade.json"
def tlo():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
@ABH.on(events.NewMessage(pattern=r'^تداول$'))
async def trade(event):
    if not event.is_group:
        return
    type = "تداول"
    await botuse(type)
    user_id = str(event.sender_id)
    gid = str(event.chat_id)
    user_data = tlo()
    last_play_time = user_data.get(user_id, {}).get("last_play_time", 0)
    current_time = int(time.time())
    time_diff = current_time - last_play_time
    if time_diff < 10 * 60:
        remaining = 10 * 60 - time_diff
        minutes = remaining // 60
        seconds = remaining % 60
        formatted_time = f"{minutes:02}:{seconds:02}"
        await event.reply(f"يجب عليك الانتظار {formatted_time} قبل التداول مجددًا.")
        return
    if user_id not in points or gid not in points[user_id]:
        await event.reply("ماعندك فلوس 💔.")
        return
    user_points = points[user_id][gid]["points"]
    if user_points < 1000:
        await event.reply(
            f"ماتكدر تتداول حاليا 💔\n"
            f"رصيدك الحالي {user_points} نقطة.\n"
            f"يجب أن يكون رصيدك 1000 نقطة على الأقل للتداول."
        )
        return
    f = user_points // 5
    r = random.randint(-50, 75)
    if r > 0:
        profit = int(f * (100 + r) / 100)
        points[user_id][gid]["points"] += profit
        await event.reply(
            f"تم التداول بنجاح \n نسبة نجاح {r}% \n فلوس الربح `{profit}` نقطة 🎉\n"
        )
    else:
        loss = int(f * (100 + r) / 100)
        points[user_id][gid]["points"] -= abs(loss)
        await event.reply(
            f"تداول بنسبة فاشلة {r}% \n خسرت `{abs(loss)}` نقطة 💔\n"
        )
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["last_play_time"] = current_time
    save_user_data(user_data)
@ABH.on(events.NewMessage(pattern=r'^شراء حل\s+(.+)$'))
async def buy(event):
    if not event.is_group:
        return
    type = "شراء حل"
    await botuse(type)
    user_id = event.sender_id
    gid = event.chat_id
    type = event.pattern_match.group(1).strip()
    valid_types = {
        'كرة قدم': 999,
        '/football': 999,
        '/quist': 250,
        '/sport': 300,
    }
    if type not in valid_types:
        await event.reply('ماكو هيج لعبة')
        return
    user_points = points[str(user_id)][str(gid)]["points"]
    price = valid_types[type]
    if user_points < price:
        await event.reply(f'عزيزي سعر الشراء {price} وانت ماعندك هلمبغ.')
        return
    points[str(user_id)][str(gid)]['points'] -= price
    await event.reply(f'تم خصم منك {price} وارسال الحل في الخاص 😀')
    if type in {'كرة قدم', '/football'}:
        r = random.choice(football)
        answer = r.get('answer', 'ما محدد الجواب')
        photo_ref = r.get('photo')
        if not photo_ref or not isinstance(photo_ref, str) or "/" not in photo_ref:
            await event.reply("حدث خطأ في تحديد صورة السؤال.")
        else:
            message_id = int(photo_ref.split("/")[-1])
            message = await ABH.get_messages("LANBOT2", ids=message_id)
            if message and message.media:
                file_path = await ABH.download_media(message.media)
                if isinstance(answer, list):
                    answer = "\n".join(map(str, answer))
                await ABH.send_file(user_id, file_path, caption=answer, parse_mode=None)
            else:
                await event.reply("لم أتمكن من العثور على الصورة.")
    else:
        await event.reply("نوع السؤال غير مدعوم حالياً.")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            await event.reply("تعذر إرسال الوسائط.")
USER_DATA_FILE = "boxing.json"
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
@ABH.on(events.NewMessage(pattern=r'مضاربة (\d+)'))
async def boxing(event):
    if not event.is_group:
        return
    type = "مضاربة"
    await botuse(type)
    reply = await event.get_reply_message()
    if not reply:
        await event.reply('عزيزي، لازم ترد على رسالة الشخص اللي تريد تضاربه.')
        return
    try:
        count = int(event.pattern_match.group(1))
    except ValueError:
        await event.reply('تأكد من كتابة رقم صحيح بعد كلمة مضاربة.')
        return
    if count <= 2999:
        await event.reply('المبلغ يجب أن يكون أكبر من 3000.')
        return
    user1_id = reply.sender_id
    user2_id = event.sender_id
    gid = str(event.chat_id)
    user_data = load_user_data()
    current_time = int(time.time())
    last_target_time = user_data.get(str(user1_id), {}).get("boxed", 0)
    if current_time - last_target_time < 10 * 60:
        remaining = 10 * 60 - (current_time - last_target_time)
        minutes = remaining // 60
        seconds = remaining % 60
        s = await event.get_sender()
        x = await mention(s)
        await event.reply(f"لا يمكن مضاربة {x} الآن، انتظر {minutes:02}:{seconds:02} دقيقة.")
        return
    last_attack_time = user_data.get(str(user2_id), {}).get("attacked", 0)
    if current_time - last_attack_time < 10 * 60:
        remaining = 10 * 60 - (current_time - last_attack_time)
        minutes = remaining // 60
        seconds = remaining % 60
        await event.reply(f"يجب عليك الانتظار {minutes:02}:{seconds:02} قبل أن تبدأ مضاربة جديدة.")
        return
    if str(user1_id) not in points or gid not in points[str(user1_id)]:
        await event.reply('الشخص الذي تم الرد عليه لا يملك نقاط.')
        return
    if str(user2_id) not in points or gid not in points[str(user2_id)]:
        await event.reply('أنت لا تملك نقاط.')
        return
    mu1 = points[str(user1_id)][gid]['points']
    mu2 = points[str(user2_id)][gid]['points']
    if count > mu1:
        await event.reply('فلوس الشخص الذي تم الرد عليه أقل من مبلغ المضاربة.')
        return
    if count > mu2:
        await event.reply('فلوسك أقل من مبلغ المضاربة.')
        return
    user1_entity = await ABH.get_entity(user1_id)
    user2_entity = await ABH.get_entity(user2_id)
    mention1 = f"[{user1_entity.first_name}](tg://user?id={user1_id})"
    mention2 = f"[{user2_entity.first_name}](tg://user?id={user2_id})"
    winner_id = random.choice([user1_id, user2_id])
    loser_id = user2_id if winner_id == user1_id else user1_id
    points[str(winner_id)][gid]['points'] += count
    points[str(loser_id)][gid]['points'] -= count
    with open("points.json", "w", encoding="utf-8") as f:
        json.dump(points, f, ensure_ascii=False, indent=2)
    winner_name = mention1 if winner_id == user1_id else mention2
    await event.reply(
        f"🥊 تمت المضاربة!\n\n"
        f"👤 {mention2} 🆚 {mention1}\n\n"
        f"🏆 الفائز: {winner_name}\n"
        f"💰 الجائزة: {count} نقطة 🎉"
    )
    user_data[str(user1_id)] = user_data.get(str(user1_id), {})
    user_data[str(user1_id)]["boxed"] = current_time
    user_data[str(user2_id)] = user_data.get(str(user2_id), {})
    user_data[str(user2_id)]["attacked"] = current_time
    save_user_data(user_data)
user_state = {}
@ABH.on(events.NewMessage(pattern='/football|كرة قدم'))
async def answer_football(event):
    if not event.is_group:
        return
    type = "/football"
    await botuse(type)
    sender = await event.get_sender()
    a = event.id
    user_id = sender.id
    r = random.choice(football)
    user_state[user_id] = {'answer': r['answer']
    }
    message_id = int(r['photo'].split("/")[-1])
    message = await ABH.get_messages("LANBOT2", ids=message_id)
    if message and message.media:
        file_path = await ABH.download_media(message.media)
        await ABH.send_file(event.chat_id, file_path, caption=r['caption'], reply_to=a)
    if os.path.exists(file_path):
        os.remove(file_path)
@ABH.on(events.NewMessage)
async def answer_handler(event):
    sender = await event.get_sender()
    user_id = sender.id if sender else event.sender_id
    msg = event.raw_text.strip()
    if msg.startswith('/') or msg == 'كرة قدم':
        return
    if user_id in user_state:
        correct_answer = user_state[user_id]['answer']
        if msg == correct_answer:
            amount = 250
            await event.reply(f"اجابة صحيحة ربحت ↢ `{amount}`")
            user_id = event.sender_id
            gid = event.chat_id
            add_points(user_id, gid, points, amount=amount)
        else:
            await event.reply("اجابة خاطئة!")
        del user_state[user_id]
WIN_VALUES = {
    "🎲": 6,
    "🎯": 6,
    "⚽": 5,
    "🎳": 6,
    "🎰": 64
}
USER_DATA_FILE = "user_data.json"
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
@ABH.on(events.NewMessage(pattern=r'.*'))
async def telegramgames(event):
    if not event.message.dice or not event.is_group:
        return    
    type = "المقدار المميز"
    await botuse(type)
    user_id = event.sender_id
    dice = event.message.dice
    emoji = dice.emoticon
    value = dice.value
    if value == 64:
        amount = random.choice([1000, 2000, 3000])
    else:
        amount = 999
    user_data = load_user_data()
    last_play_time = user_data.get(str(user_id), {}).get("last_play_time", 0)
    current_time = int(time.time())
    time_diff = current_time - last_play_time
    if time_diff < 5 * 60:
        remaining = 5 * 60 - time_diff
        minutes = remaining // 60
        seconds = remaining % 60
        formatted_time = f"{minutes:02}:{seconds:02}"
        await event.reply(f" يجب عليك الانتظار {formatted_time} قبل اللعب مجددًا.")
        return
    await asyncio.sleep(4)
    win = value == WIN_VALUES.get(emoji, -1)
    if win:
        await event.reply(f"اررررحب فزت ب {emoji}  تم اضافة ( `{amount}` ) لثروتك")
        user_id = event.sender_id
        gid = event.chat_id
        add_points(user_id, gid, points, amount=amount)
    else:
        await event.reply(f"للاسف خسرت ب {emoji}\n المقدار: `{value}`")
    user_data[str(user_id)] = {"last_play_time": current_time}
    save_user_data(user_data)
@ABH.on(events.NewMessage(pattern='/num'))
async def num(event):
    if not event.is_group:
        return
    await botuse("/num")
    num = random.randint(1, 10)
    max_attempts = 3
    async with ABH.conversation(event.chat_id, timeout=6) as conv:
        name = await mention(event)
        uid = event.sender_id
        if uid != event.sender_id:
            return
        await conv.send_message(f'اهلا {name} تم بدء اللعبه , حاول تخمين الرقم من 10 الئ 1', file='https://t.me/VIPABH/1204', reply_to=event.message.id)
        for attempt in range(1, max_attempts + 1):
            try:
                response = await conv.get_response()
                get = response.text.strip()
                try:
                    guess = int(get)
                except ValueError:
                    continue
                if guess == num:
                    msg = await conv.send_message("🎉")
                    await asyncio.sleep(3)
                    await msg.edit('🎉 مُبارك! لقد فزت!')
                    return
                else:
                    if attempt < max_attempts:
                        await conv.send_message(f"جرب مرة أخرى، الرقم غلط💔")
                    else:
                        await conv.send_message(f'للأسف، لقد نفدت محاولاتك. الرقم الصحيح هو {num}')
            except asyncio.TimeoutError:
                await conv.send_message(f'انتهى الوقت! لم تقم بإرسال إجابة في الوقت المحدد. {name}', reply_to=event.message.id)
                return
@ABH.on(events.NewMessage(pattern='/ارقام'))
async def show_number(event):
    if not event.is_group:
        return
    if num:
        await ABH.send_message(wfffp, f" الرقم السري هو: {num}")
        await event.reply("تم إرسال الرقم السري إلى @k_4x1.")
    else:
        await event.reply("لم تبدأ اللعبة بعد. أرسل /num لبدء اللعبة.")
group_game_status = {}
number2 = None
game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
numbers_board = [["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]]
original_game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
def format_board(game_board, numbers_board):
    formatted_board = ""
    formatted_board += " ".join(numbers_board[0]) + "\n"
    formatted_board += " ".join(game_board[0]) + "\n"
    return formatted_board
def reset_game(chat_id):
    global game_board, number2, group_game_status
    game_board = [row[:] for row in original_game_board]
    number2 = None
    group_game_status[chat_id]['game_active'] = False
    group_game_status[chat_id]['active_player_id'] = None
group_game_status = {}
@ABH.on(events.NewMessage(pattern='/rings|محيبس'))
async def rings(event):
    if not event.is_group:
        return
    type = "/rings"
    await botuse(type)
    username = event.sender.username or "x04ou"
    markup = [[Button.inline("ابدأ اللعبة", b"startGame")]]
    await event.reply(
        f"أهلاً [{event.sender.first_name}](https://t.me/{username})! حياك الله. اضغط على الزر لبدء اللعبة.",
        file="https://t.me/VIPABH/1210",  
        parse_mode="Markdown",
        buttons=markup
    )
@ABH.on(events.CallbackQuery(func=lambda call: call.data == b"startGame"))
async def handle_rings(event):
    global number2
    chat_id = event.chat_id
    user_id = event.sender_id
    username = event.sender.username or "x04ou"
    if chat_id not in group_game_status:
        group_game_status[chat_id] = {'game_active': False, 'active_player_id': None}    
    if not group_game_status[chat_id]['game_active']:
        group_game_status[chat_id]['game_active'] = True
        group_game_status[chat_id]['active_player_id'] = user_id
        number2 = random.randint(1, 6)
        group_game_status[chat_id]['number2'] = number2
        await event.edit(buttons=None)
        await event.respond(
            f"عزيزي [{event.sender.first_name}](https://t.me/@{username})! تم تسجيلك في لعبة محيبس \nارسل `جيب ` + رقم للحزر \n ارسل `طك ` + رقم للتخمين.",
            parse_mode="Markdown"
        )
number2 = None
game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
numbers_board = [["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]]
original_game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
def format_board(game_board, numbers_board):
    formatted_board = ""
    formatted_board += " ".join(numbers_board[0]) + "\n"
    formatted_board += " ".join(game_board[0]) + "\n"
    return formatted_board
def rest_game(chat_id):
    global game_board, number2, group_game_status
    game_board = [row[:] for row in original_game_board]
    number2 = None
    group_game_status[chat_id]['game_active'] = False
    group_game_status[chat_id]['active_player_id'] = None
group_game_status = {}
@ABH.on(events.NewMessage(pattern=r'جيب (\d+)'))
async def handle_guess(event):
    if not event.is_group:
        return
    global number2, game_board, points, group_game_status
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            guess = int(event.text.split()[1])  
            if 1 <= guess <= 6:  
                if guess == number2:
                    n = event.sender.first_name
                    game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                    gid = event.chat_id
                    p = random.randint(10, 50)
                    user_id = event.sender_id
                    add_points(user_id, gid, points, amount=p)
                    m = {points[str(user_id)][str(gid)]["points"]}
                    await event.reply(
                        f'🎉 مبارك، اللاعب ({n}) وجد المحبس 💍!\n'
                        f'{format_board(game_board, numbers_board)}\n'
                        f'فلوسك ↞ `( {m} )`')
                    rest_game(chat_id)
                else: 
                    n = event.sender.first_name
                    game_board = [["❌" if i == guess - 1 else "🖐️" for i in range(6)]]
                    await event.reply(f"ضاع البات ماضن بعد تلگونة ☹️ \n{format_board(game_board, numbers_board)}")
                    rest_game(chat_id)
            else:
                await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
        except (IndexError, ValueError):
            await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
@ABH.on(events.NewMessage(pattern=r'طك (\d+)'))
async def handle_strike(event):
    if not event.is_group:
        return
    global game_board, number2, group_game_status
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            strike_position = int(event.text.split()[1])  
            if strike_position == number2:
                game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                await event.reply(f"**خسرت!** \n{format_board(game_board, numbers_board)}")
                rest_game(chat_id)
            else:
                abh = [
                    "تلعب وخوش تلعب 👏🏻",
                    "لك عاش يابطل استمر 💪🏻",
                    "على كيفك ركزززز انتَ كدها 🤨",
                    "لك وعلي ذيييب 😍"
                ]
                iuABH = random.choice(abh)
                game_board[0][strike_position - 1] = '🖐️'
                await event.reply(f" {iuABH} \n{format_board(game_board, numbers_board)}")
        except (IndexError, ValueError):
            await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
@ABH.on(events.NewMessage(pattern='/محيبس'))
async def show_number(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        target_user_id = 1910015590  
        await ABH.send_message(target_user_id, f"الرقم السري هو: {number2}")
        await event.reply("تم إرسال الرقم السري إلى @k_4x1.")
    else:
        await event.reply("لم تبدأ اللعبة بعد. أرسل /rings لبدء اللعبة.")
games = {}
@ABH.on(events.NewMessage(pattern='اكس او|/xo|/Xo'))
async def xo(event):
    if not event.is_group:
        return
    type = "اكس او"
    await botuse(type)
    chat_id = event.chat_id
    player1_id = event.sender_id
    username1 = event.sender.username or "x04ou"
    t1 = event.sender.first_name or "x04ou"
    games[chat_id] = {
        "player1": player1_id,
        "player2": None,
        "username1": username1,
        "username2": None,
        "t1": t1,
        "t2": None,
        "turn": None,
        "board": [" "] * 9,
        "restart_confirmations": {}
    }
    markup = [[Button.inline("ابدأ اللعبة", b"start")]]
    await event.reply(
        f"أهلاً [{t1}](https://t.me/{username1})! تم تسجيلك في لعبة X/O، أنت اللاعب الأول ودورك هو X.",
        file="https://t.me/VIPABH/1216",
        parse_mode="md",
        buttons=markup
    )
@ABH.on(events.CallbackQuery(func=lambda e: e.data == b"start"))
async def start_game(event):
    chat_id = event.chat_id
    if chat_id not in games:
        return
    game = games[chat_id]
    player2_id = event.sender_id
    if player2_id == game["player1"]:
        await event.answer("لا يمكنك اللعب ضد نفسك.")
        return
    game["player2"] = player2_id
    game["username2"] = event.sender.username or "x04ou"
    game["t2"] = event.sender.first_name or "x04ou"
    game["turn"] = game["player1"]
    await show_board(event, chat_id)
async def show_board(event, chat_id, winner=None):
    game = games[chat_id]
    board = game["board"]
    markup = [
        [Button.inline(board[0], b"move_0"), Button.inline(board[1], b"move_1"), Button.inline(board[2], b"move_2")],
        [Button.inline(board[3], b"move_3"), Button.inline(board[4], b"move_4"), Button.inline(board[5], b"move_5")],
        [Button.inline(board[6], b"move_6"), Button.inline(board[7], b"move_7"), Button.inline(board[8], b"move_8")]
    ]
    if winner:
        p = random.randint(50, 500)
        add_points(event.sender_id, chat_id, points, amount=p)
        await event.edit(
            f"اللاعب [{winner['name']}](https://t.me/{winner['username']}) فاز باللعبة! وتمت إضافة `{p}` فلوس.",
            buttons=[[Button.inline("إعادة", b"restart"), Button.inline("إلغاء", b"cancel")]],
            parse_mode="md"
        )
        del games[chat_id]
    elif " " not in board:
        await event.edit("اللعبة انتهت بالتعادل!", buttons=[[Button.inline("إعادة", b"restart"), Button.inline("إلغاء", b"cancel")]])
        del games[chat_id]
    else:
        current_id = game["turn"]
        current_name = game["t1"] if current_id == game["player1"] else game["t2"]
        current_username = game["username1"] if current_id == game["player1"] else game["username2"]
        try:
            await event.edit(
                f"اللاعب الأول: [{game['t1']}](https://t.me/{game['username1']})\n"
                f"اللاعب الثاني: [{game['t2']}](https://t.me/{game['username2']})\n\n"
                f"دور: [{current_name}](https://t.me/{current_username})",
                buttons=markup,
                parse_mode="md"
            )
        except:
            await event.reply("خطأ في عرض اللوحة، حاول مجددًا.")
@ABH.on(events.CallbackQuery(func=lambda e: e.data.startswith(b"move_")))
async def handle_move(event):
    chat_id = event.chat_id
    game = games.get(chat_id)
    if not game:
        return
    move_index = int(event.data.decode().split("_")[1])
    if game["board"][move_index] != " ":
        await event.answer("المربع مشغول!")
        return
    current_id = event.sender_id
    if current_id != game["turn"]:
        await event.answer("ليس دورك الآن!")
        return
    symbol = "X" if current_id == game["player1"] else "O"
    game["board"][move_index] = symbol
    game["turn"] = game["player2"] if current_id == game["player1"] else game["player1"]
    winner = check_winner(game["board"])
    if winner:
        winner_name = game["t1"] if winner == "X" else game["t2"]
        winner_username = game["username1"] if winner == "X" else game["username2"]
        await show_board(event, chat_id, winner={"name": winner_name, "username": winner_username})
    else:
        await show_board(event, chat_id)
def check_winner(board):
    lines = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None
@ABH.on(events.CallbackQuery(func=lambda e: e.data == b"restart"))
async def restart(event):
    chat_id = event.chat_id
    game = games.get(chat_id)
    if not game:
        return
    uid = event.sender_id
    game["restart_confirmations"][uid] = True
    if game["player1"] in game["restart_confirmations"] and game["player2"] in game["restart_confirmations"]:
        game["board"] = [" "] * 9
        game["turn"] = game["player1"]
        game["restart_confirmations"] = {}
        await show_board(event, chat_id)
    else:
        await event.answer("بانتظار موافقة اللاعب الآخر")
@ABH.on(events.CallbackQuery(func=lambda e: e.data == b"cancel"))
async def cancel(event):
    chat_id = event.chat_id
    if chat_id in games:
        del games[chat_id]
    await event.edit("تم إلغاء اللعبة.")
questions_and_answers_q = [
    {"question": "من هم ال البيت؟", "answer": ["هم اهل بيت رسول الله", 'اهل بيت رسول الله', "ال بيت رسول الله"]},
    {"question": "من هو الخليفة الاول؟", "answer": ["ابا الحسن علي", "الامام علي", "علي ابن ابي طالب"]},
    {"question": "كم عدد المعصومين؟", "answer": ["14", "اربع عشر"]},
    {"question": "كم عدد اهل البيت؟", "answer": ["12", "اثنا عشر"]},
    {"question": "ال**** هو نقل الكلام من ثقات الحديث", "answer": [ "التواتر", "تواتر"]},
    {"question": "من هو الدنيئ الذي غدر الامام علي بالمسجد يوم 19 رمضان؟", "answer": ["اللعين ابن ملجم", "ابن ملجم", "عبد الرحمن", "عبد الرحمن ابن ملجم"]},
    {"question": "من الذي قال يا ابن راعية المعزة وعلئ من؟", "answer": "الامام الحسين الشمر اللعين"},
    {"question": "الامام الذي بعد الامام علي؟", "answer": ["الحسن المجتبى", "الحسن", "الامام الحسن"]},
    {"question": "الامام الذي بعد الامام الحسن؟", "answer": ["الحسين الشهيد", "الامام الحسين"]},
    {"question": "بحق من نزلت اية التطهير؟", "answer": ["ال بيت رسول الله", "اهل البيت"]},
    {"question": "من هو سيف الله المسلول؟", "answer": ["الامير علي", "الامام علي"]},
    {"question": "من هو سيف الشيطان المذلول؟", "answer": "خالد"},
    {"question": "من هم الثقلين؟", "answer": ["كتاب الله واهل البيت", "كتاب الله و اهل البيت", "كتاب الله و اهل البيت"]},
    {"question": "من هو قمر عشيرة الهواشم؟", "answer": "الامام العباس"},
    {"question": "من هو كفيل زينب؟", "answer": "الامام العباس"},
    {"question": "من الذي قتل المحسن ابن علي؟", "answer": ["اللعين عمر", "عمر"]},
    {"question": "من هو قطيع الكفين؟", "answer": "الامام العباس"},
    {"question": "من هو شاعر قصيدة الله يا حامي الشريعة؟", "answer": "حيدر الحلي"},
    {"question": "من هو حامي الجار؟", "answer": "الامام علي"},
    {"question": "من صاحب قول \n أَمْلَأَ رُكابِي فِضَّةً أَوْ ذَهَبًا إِنِّي قَتَلْتُ خَيْرَ الرِّجَالِ أَمَّا وَأَبَا؟", "answer": "سنان بن انس"},
    {"question": "من هو سلمان المحمدي؟", "answer": "صحابي النبي و شهيد كربلاء"},
    {"question": "من هو الذي دفن مع الامام الحسين؟", "answer": "عبد الله الرضيع"},
    {"question": "ما هي اسم الواقعه في يوم العاشر من محرم؟", "answer": "واقعة الطف"},
    {"question": "ما هو اسم اليوم الذي استشهد فيه الامام الحسين؟", "answer": "عاشوراء"},
    {"question": "من هو الحجة المنتظر؟", "answer": "الامام المهدي"},
    {"question": "كم عدد المعصومين الذي اسمهم محمد؟", "answer": "2"},
    {"question": "ما هو اسم الامام المهدي؟", "answer": "محمد ابن الحسن"},
    {"question": "ما هي بيعة الغدير؟", "answer": ["تتويج الامام علي", "بيعة الامام علي"]},
    {"question": "من هو الذي تصدق في المحبس في الصلاة؟", "answer": "الامام علي"},
    {"question": "ما هو اسم المكان الذي تم تتويج الامام علي خليفة؟", "answer": "غدير خم"},
    {"question": "اين دفنت ام البنين؟", "answer": ["في البقيع", "في قبور البقيع"]},
    {"question": "متى ولادة الامام المهدي \n عجل الله فرجة الشريف؟", "answer": [" 15 من شعبان", "15 شعبان", "نصف شعبان"]},
    {"question": "من القائل , بين الحق والباطل 4 اصابع؟", "answer": "الامام علي"},
    {"question": "من هو الصادق الامين؟", "answer": "النبي محمد"},
    {"question": "من هو الرسول الاعظم؟", "answer": ["الرسول محمد" , "النبي محمد"]},
    {"question": "من هو قائد الغر المحجلين؟", "answer": "الامام علي"},
    {"question": "من قائل مثلي لا يبايع مثله؟", "answer": "الامام الحسين"},
    {"question": "الان انكسر ظهري \n قالها الحسين لكن بحق من؟", "answer": "الامام العباس"},
    {"question": "من هو الفاروق الاعظم؟", "answer": "الامام علي"},
    {"question": "من هو سيد الشهداء؟", "answer": "الامام الحسين"},
    {"question": "من هو الذي اسقط عائشة في حرب الجمل؟", "answer": "الامام الحسن"},
    {"question": "ما انصفوكِ صانوا حرائرهم واخرجوكِ \n قالها الامام علي لكن بحق من؟", "answer": "عائشة"},
    {"question": "الخسف في البيداء هي علامة من علامات؟", "answer": "ظهور الامام"},
    {"question": "من هو عليل كربلاء؟", "answer": ["الامام السجاد", "الامام زين العابدين"]},
    {"question": "من الاعظم النبوة ام الامامة؟", "answer": "الامامة"},
    {"question": "من هو عميد المنبر الحسيني؟", "answer": "احمد الوائلي"},
    {"question": "من هو زعيم الحوزه العلمية؟", "answer": ["ابو القاسم الخوئي", "الخوئي"]},
    {"question": "ما هو حكم التطبير حسب قول العلماء؟", "answer": "حلال"},
    {"question": "ما هو حكم سماع الاغاني؟", "answer": "حرام"},
    {"question": "ما هو حكم التدخين؟", "answer": "حلال"},
    {"question": "من هو عون؟", "answer": "ابن السيدة زينب"},
    {"question": "من المنتصر في حرب الجمل؟", "answer": "الامام علي"},
    {"question": "كم عدد الخوارج في واقعةالطف؟", "answer": ["70 الف", "سبعين الف", "سبعون الف"]},
    {"question": "من هو مفرح قلب الزهراء؟", "answer": "ابو لؤلؤة"}
]
states = {}
@ABH.on(events.NewMessage(pattern='اسئلة|/quist'))
async def quest(event):
    if not event.is_group:
        return
    type = "/quist"
    await botuse(type)
    """بدء السؤال العشوائي"""
    user_id = event.sender_id
    quest = random.choice(questions_and_answers_q)
    states[user_id] = {
        "question": quest,
        "waiting_for_answer": True,
        "start_time": time.time()
    }
    await event.reply(f"{quest['question']}")
@ABH.on(events.NewMessage)
async def check_quist(event):
    if not event.text:
        return
    user_id = event.sender_id
    usermessage = event.text.strip()
    gid = event.chat_id
    if user_id in states and states[user_id].get("waiting_for_answer"):
        question_q = states[user_id].get("question", {})
        answers_q = question_q.get('answer', [])
        start_time = states[user_id].get("start_time")
        current_time = time.time()
        time_passed = current_time - start_time
        if time_passed > 60:
            del states[user_id]
            return
        if usermessage in answers_q:
            p = random.randint(50, 500)
            add_points(user_id, gid, points, amount=p)
            await event.reply(
                f"هلا هلا طبوا الشيعة 🫡 \n ربحت (`{p}`) \n فلوسك ↢ {points[str(user_id)][str(gid)]['points']}"
            )
            del states[user_id]
        else:
            pass
questions_and_answers = [
    {"question": "أين أقيمت بطولة كأس العالم لكرة القدم عام 2002؟", "answer": ["كوريا الجنوبية واليابان", 'كوريا الجنوبية و اليابان']},
    {"question": "من هو اللاعب المعروف بأنه الهداف الأول في دوري أبطال أوروبا؟", "answer": ["كريستيانو رونالدو", 'رونالدو', "كرستيانو"]},
    {"question": "من اللاعب الحاصل على جائزة الكرة الذهبية في عام 2015م؟", "answer": ["كريستيانو رونالدو", 'رونالدو', "كرستيانو"]},
    {"question": "من هو اللاعب الذي حصل على جائزة أفضل لاعب في أوروبا لعام 2020؟", "answer": ["روبرت ليفاندوفسكي", 'ليفاندوفسكي']},
    {"question": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في موسم واحد بالدوري الإنجليزي الممتاز؟", "answer": ["محمد صلاح"]},
    {"question": "ما هو النادي الذي حقق دوري أبطال أوروبا ثلاث مرات متتالية في الفترة الحديثة؟", "answer": ["ريال مدريد"]},
    {"question": "ما هو النادي الذي حقق أكبر عدد من البطولات في الدوري الإنجليزي الممتاز؟", "answer": ["مانشستر يونايتد"]},
    {"question": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في نسخة واحدة من كأس العالم؟", "answer": ["جاست فونتين"]},
    {"question": "من هو المدرب الذي قاد تشيلسي للفوز بدوري أبطال أوروبا 2021؟", "answer": ["توخيل", "توماس توخيل"]},
    {"question": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ الدوري الألماني؟", "answer": ["غيرد مولر"]},
    {"question": "من هو اللاعب الذي حصل على جائزة الحذاء الذهبي في كأس العالم 2014؟", "answer": ["رودريغيز"]},
    {"question": "من هو أكثر لاعب سجل أهدافاً في تاريخ كرة القدم؟", "answer": ["بيليه", "كريستيانو رونالدو"]},
    {"question": "من هو اللاعب الذي حصل على جائزة أفضل لاعب في أفريقيا لعام 2019؟", "answer": ["ساديو ماني"]},
    {"question": "ما هو النادي الذي حقق أكبر عدد من البطولات في الدوري الفرنسي؟", "answer": ["سانت إتيان"]},
    {"question": "كم عدد ألقاب الدوري الإنجليزي التي حققها مانشستر سيتي حتى 2024؟", "answer": ["9", "تسعة"]},
    {"question": "ما هو النادي الذي حقق أكبر عدد من البطولات في الدوري الإسباني؟", "answer": ["ريال مدريد"]},
    {"question": "من هو المدرب الذي قاد إسبانيا للفوز بكأس العالم 2010؟", "answer": ["فيسنتي ديل بوسكي"]},
    {"question": "كم عدد ألقاب ريال مدريد في دوري أبطال أوروبا حتى 2024؟", "answer": ["14", "أربعة عشر"]},
    {"question": "من هو اللاعب الذي حصل على جائزة أفضل لاعب في كأس العالم 2018؟", "answer": ["مودريتش"]},
    {"question": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ كأس العالم؟", "answer": ["كلوزه"]},
    {"question": "كم عدد الكرات الذهبية التي حصل عليها كريستيانو رونالدو؟", "answer": ["5", "خمسة"]},
    {"question": "كم عدد ألقاب كأس أمم أوروبا التي فاز بها منتخب ألمانيا؟", "answer": ["3", "ثلاثة"]},
    {"question": "ما هو أكبر ملعب لكرة القدم في العالم من حيث السعة؟", "answer": ["ملعب رونغرادو"]},
    {"question": "من هو اللاعب الذي سجل أسرع هاتريك في الدوري الإنجليزي؟", "answer": ["ساديو ماني"]},
    {"question": "من هو المدرب الذي قاد منتخب ألمانيا للفوز بكأس العالم 2014؟", "answer": ["لوف"]},
    {"question": "ما هي الدولة التي فازت بأكبر عدد من بطولات كأس العالم؟", "answer": ["البرازيل"]},
    {"question": "كم عدد بطولات كأس العالم التي فاز بها منتخب البرازيل؟", "answer": ["5", "خمسة"]},
    {"question": "ما هي الدولة التي فازت ببطولة كأس الأمم الأوروبية 2016؟", "answer": ["البرتغال"]},
    {"question": "ما هو النادي الذي يُعرف بلقب 'الشياطين الحمر'؟", "answer": ["مانشستر يونايتد"]},
    {"question": "من هو اللاعب الذي يُلقب بـ'البرغوث'؟", "answer": ["ليونيل ميسي", 'ميسي', "مسي"]},
    {"question": "متى سجل دييجو مارادونا هدفه الشهير باليد في كأس العالم؟", "answer": ["1986"]},
    {"question": "كم مرة فاز ليونيل ميسي بكأس العالم؟", "answer": ["1", "واحدة", "مرة واحدة"]},
    {"question": "في أي سنة حقق ليفربول لقب البريميرليج بعد غياب 30 سنة؟", "answer": ["2020"]},
    {"question": "من هو أكثر لاعب تتويجًا بدوري أبطال أوروبا؟", "answer": ["فرانشيسكو خينتو"]},
    {"question": "من هو اللاعب الذي سجل أسرع هدف في تاريخ كأس العالم؟", "answer": ["هاكان"]},
    {"question": "ما هي الدولة التي فازت بأول بطولة لكأس العالم؟", "answer": ["الاورغواي"]},
    {"question": "كم مرة فاز المنتخب السعودي بكأس آسيا لكرة القدم؟", "answer": ["3 مرات"]},
    {"question": "ما هو النادي الأكثر تحقيقًا للبطولات في العالم؟", "answer": ["ريال مدريد"]},
    {"question": "من هو النادي الأكثر مشاركة في الدوري الأوروبي؟", "answer": ["ريال مدريد"]},
    {"question": "ما هي الدولة التي فازت ببطولة كوبا أمريكا 2019؟", "answer": ["البرازيل"]},
    {"question": "من هو اللاعب الذي يُلقب بـ'الفتى الذهبي'؟", "answer": ["دييغو مارادونا"]},
    {"question": "ما هي الدولة التي ظهرت فيها كرة القدم لأول مرة؟", "answer": ["إنجلترا"]},
    {"question": "من هو اللاعب الذي يُعرف بلقب 'الملك' في كرة القدم؟", "answer": ["بيليه"]},
    {"question": "من هو أكثر مدرب فاز بدوري أبطال أوروبا؟", "answer": ["كارلو أنشيلوتي"]},
    {"question": "من هو اللاعب الذي يُعرف بلقب 'المايسترو'؟", "answer": ["أندريا بيرلو"]},
    {"question": "ما هي الدولة التي استضافت كأس العالم 2010؟", "answer": ["افريقيا"]},
    {"question": "من هو اللاعب الأكثر مشاركة في تاريخ كأس العالم؟", "answer": ["ميسي"]},
    {"question": "ما هي الدولة التي استضافت كأس العالم 2006؟", "answer": ["ألمانيا"]},
    {"question": "أي نادي يُعرف بلقب الشياطين الحمر؟", "answer": ["مانشستر يونايتد"]},
    {"question": "من هو صاحب أشهر هدف باليد في كأس العالم؟", "answer": ["مارادونا"]},
    {"question": "من هو اللاعب الذي يُعرف بلقب 'الماجيك'؟", "answer": ["رونالدينيو"]},
    {"question": "ما هي الدولة التي استضافت كأس العالم 1998؟", "answer": ["فرنسا"]},
    {"question": "متى أقيمت أول بطولة لكأس العالم لكرة القدم؟", "answer": ["1930"]},
    {"question": "ما هو تاريخ أول كأس عالم ومتى أقيم لأول مرة؟", "answer": ["1930"]},
    {"question": "أي منتخب فاز بأول نسخة من كأس العالم؟", "answer": ["الأوروغواي"]},
    {"question": "من هو أول لاعب فاز بالكرة الذهبية؟", "answer": ["ستانلي ماثيوس"]},
    {"question": "من هو اللاعب الذي يُعرف بلقب 'الظاهرة'؟", "answer": ["رونالدو"]},
    {"question": "ما هو النادي الذي يُعرف بلقب 'العجوز'؟", "answer": ["يوفنتوس"]},
    {"question": "ما هو النادي الذي يُعرف بلقب 'الريدز'؟", "answer": ["ليفربول"]},
    {"question": "كم مرة فاز ميلان بدوري أبطال أوروبا؟", "answer": ["7", "سبعة"]},
    {"question": "ما هو النادي الذي يُعرف بلقب 'البلوز'؟", "answer": ["تشيلسي"]},
    {"question": "أي فريق فاز بدوري أبطال أوروبا 2015؟", "answer": ["برشلونة"]},
    {"question": "ما هو النادي الذي يُعرف بلقب 'النسور'؟", "answer": ["لاتسيو"]},
    {"question": "في أي دولة أقيم كأس العالم الأول؟", "answer": ["الاورغواي"]},
    {"question": "أي فريق يُعرف بلقب السيدة العجوز؟", "answer": ["يوفنتوس"]},
    {"question": "أي دولة استضافت كأس العالم 2014؟", "answer": ["البرازيل"]},
    {"question": "المنتخب الاكثر فوز ب كأس العالم؟", "answer": ["البرازيل"]},
    {"question": "فريق كرة القدم يتكون من كم لاعب؟", "answer": ["11 لاعب"]},
    {"question": "أي منتخب يُعرف بلقب التانغو؟", "answer": ["الأرجنتين"]},
    {"question": "من هو هداف كأس العالم 2002؟", "answer": ["رونالدو"]},
    {"question": "من اللاعب الذي يُلقب بالبرغوث؟", "answer": ["ميسي"]},
    {"question": "أي فريق يُعرف بلقب البلوز؟", "answer": ["تشيلسي"]},
    {"question": "أي منتخب يُعرف بلقب الديوك؟", "answer": ["فرنسا"]},
    {"question": "من هو ال GOAT؟", "answer": ["رونالدو"]},
    {"question": "من هو عم برسا؟", "answer": ["رونالدو"]}
]
user_states_s = {}
@ABH.on(events.NewMessage(pattern='كره قدم|كرة القدم|/sport'))
async def sport(event):
    if not event.is_group:
        return
    type = "/sport"
    await botuse(type)
    user_id = event.sender_id
    question = random.choice(questions_and_answers)
    user_states_s[user_id] = {
        "question": question,
        "waiting_for_answer": True
    }
    await event.reply(f"{question['question']}")
@ABH.on(events.NewMessage)
async def check_sport(event):
    if not event.text:
        return
    user_id = event.sender_id
    user_message = event.text.strip()
    gid = event.chat_id
    if user_id in user_states_s and user_states_s[user_id].get("waiting_for_answer"):
        current_question = user_states_s[user_id].get("question", {})
        correct_answers = current_question.get('answer', [])
        if user_message in correct_answers:
            p = random.randint(50, 500)
            add_points(user_id, gid, points, amount=p)
            await event.reply(f"احسنت اجابة صحيحة 🫡 \n ربحت (`{p}`) \n فلوسك ↢ {points[str(user_id)][str(gid)]['points']}")
            del user_states_s[user_id]
        else:
            pass
choices = {"rock": "🪨 حجرة", "paper": "📜 ورقة", "cuter": "✂️ مقص"}
active_games = {}
@ABH.on(events.NewMessage(pattern=r"^(حجرة|/rock)$"))
async def rock_handler(event):
    if not event.is_group:
        return
    type = "حجرة"
    await botuse(type)
    chat_id = event.chat_id
    sender = await event.get_sender()
    reply = await event.get_reply_message()
    if reply and reply.sender_id != sender.id:
        opponent = await reply.get_sender()
        game_type = "pvp"
        name1 = sender.first_name
        name2 = opponent.first_name
        player2_id = opponent.id
        s1 = await mention(event)
        s2 = await ment(opponent)
    else:
        me = await ABH.get_me()
        game_type = "pve"
        name1 = sender.first_name
        name2 = me.first_name
        player2_id = "bot"
        s1 = await mention(event)
        s2 = await ment(me)
    active_games[chat_id] = {
        "player1": sender.id,
        "name1": name1,
        "player2": player2_id,
        "name2": name2,
        "type": game_type
    }
    msg = await event.respond(
        f"👊 اللاعب الأول: {s1}\n🧠 اللاعب الثاني: {s2}",
        buttons=[[Button.inline("🪨", b"rock"), Button.inline("✂️", b"cuter"), Button.inline("📜", b"paper")]],
        reply_to=event.id
    )
    active_games[chat_id]["msg_id"] = msg.id
@ABH.on(events.CallbackQuery(data=b"rock"))
async def cb_rock(event): await handle_choice(event, "rock")
@ABH.on(events.CallbackQuery(data=b"cuter"))
async def cb_cuter(event): await handle_choice(event, "cuter")
@ABH.on(events.CallbackQuery(data=b"paper"))
async def cb_paper(event): 
    await handle_choice(event, "paper")
async def handle_choice(event, user_choice_key):
    chat_id = event.chat_id
    user_id = event.sender_id
    game = active_games.get(chat_id)
    if not game:
        await event.answer(" لا توجد لعبة جارية!", alert=True)
        return
    if game["type"] == "pve":
        bot_choice_key = random.choice(list(choices.keys()))
        bot_choice = choices[bot_choice_key]
        user_choice = choices[user_choice_key]
        if user_choice_key == bot_choice_key:
            result = "🤝 تعادل"
            points = 500
        elif (
            (user_choice_key == "rock" and bot_choice_key == "cuter") or
            (user_choice_key == "paper" and bot_choice_key == "rock") or
            (user_choice_key == "cuter" and bot_choice_key == "paper")
        ):
            result = "🎉 فزت"
            points = random.randint(500, 1500)
        else:
            result = "😢 خسرت"
            points = 0
        if points > 0:
            p = random.randint(50, 500)
            add_points(user_id, chat_id, points, amount=p)
        msg = (
            f"{game['name1']} {user_choice}\n"
            f"{game['name2']} {bot_choice}\n\n"
            f"{result}"
        )
        if points > 0:
            msg += f"\n🏅 تم إضافة `{points}` نقطة"
        await event.edit(msg)
    elif game["type"] == "pvp":
        if user_id not in [game["player1"], game["player2"]]:
            await event.answer("❌ لست من ضمن اللاعبين", alert=True)
            return
        game.setdefault("choices", {})[user_id] = user_choice_key
        if len(game["choices"]) < 2:
            await event.answer(" تم حفظ اختيارك، ننتظر خصمك...", alert=True)
            return
        p1_choice = game["choices"][game["player1"]]
        p2_choice = game["choices"][game["player2"]]
        player1_name = game["name1"]
        player2_name = game["name2"]
        player1_id = game["player1"]
        player2_id = game["player2"]
        if p1_choice == p2_choice:
            result = "🤝 تعادل"
        elif (
            (p1_choice == "rock" and p2_choice == "cuter") or
            (p1_choice == "paper" and p2_choice == "rock") or
            (p1_choice == "cuter" and p2_choice == "paper")
        ):
            result = f"🎉 {player1_name} فاز"
        else:
            result = f"🎉 {player2_name} فاز"
        await event.edit(
            f"[{player1_name}](tg://user?id={player1_id}) {choices[p1_choice]}\n"
            f"[{player2_name}](tg://user?id={player2_id}) {choices[p2_choice]}\n\n"
            f"{result}"
        )
    active_games.pop(chat_id, None)
res = {}
a = 0
players = {}
answer = None
is_on = False
start_time = None
fake = Faker("ar_AA")
@ABH.on(events.NewMessage(pattern=r"(?i)^(?:اسرع|/faster)$"))  
async def faster(event):
    if not event.is_group:
        return
    type = "اسرع"
    await botuse(type)
    global is_on, players
    is_on = True
    players.clear()
    uid = event.sender_id
    sender = await event.get_sender()
    name = sender.first_name
    if uid not in players:
         players[uid] = {"username": name}
         res[name] = {"name": name, "score": 0}
         await event.reply("اهلاً ضفتك للعبة , للانضمام ارسل `انا` للبدء `تم` \n**ENJOY BABY✌**")
@ABH.on(events.NewMessage(pattern="(?i)انا$"))
async def faster_join(event):
    if not event.is_group:
        return
    if is_on:
        uid = event.sender_id
        sender = await event.get_sender()
        name = sender.first_name
        if uid not in players:
            players[uid] = {"username": name}
            res[name] = {"name": name, "score": 0}
            await event.reply('سجلتك باللعبة، لا ترسل مجددًا!')
        else:
            await event.reply("عزيزي الصديق، سجلتك والله!")
@ABH.on(events.NewMessage(pattern="(?i)الاعبين$"))
async def faster_players(event):
    if not event.is_group:
        return
    global is_on
    if is_on and players:
        player_list = "\n".join([f"{pid} - {info['username']}" for pid, info in players.items()])
        await event.reply(f"📜 قائمة اللاعبين:\n{player_list}")
        is_on = True
    else:
        await event.reply('ماكو لاعبين 🙃')
s = random.randint(6, 8)
@ABH.on(events.NewMessage(pattern="(?i)تم$"))
async def faster_done(event):
    if not event.is_group:
        return
    global answer, is_on, start_time
    if is_on:
        await event.reply('تم بدء اللعبة، انتظر ثواني...')
        await asyncio.sleep(2)
        for _ in range(5):
            word = fake.word()
            answer = (word)
            await event.respond('راقب الكلمة 👇')
            await asyncio.sleep(1)
            await event.respond(f'✍ اكتب ⤶ {answer}')
            start_time = time.time()
            await asyncio.sleep(s)
        points_list = "\n".join([f"{info['name']} - {info['score']} نقطة" for info in res.values()])
        await event.reply(f"**ترتيب اللاعبين بالنقاط**\n{points_list}")
        is_on = False
@ABH.on(events.NewMessage)
async def faster_reult(event):
    if not event.is_group:
        return
    global is_on, start_time, answer, a
    if not is_on or start_time is None:
        return
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time)
    isabh = event.text.strip()
    wid = event.sender_id
    if answer and isabh.lower() == answer.lower() and wid in players:
        username = players[wid]["username"]
        if username not in res:
            res[username] = {"name": username, "score": 0}
        res[username]["score"] += 1
        user_id = event.sender_id
        gid = event.chat_id
        p = random.randint(1, 100)
        a = points[str(user_id)][str(gid)]['points']
        await event.reply(f'احسنت جواب موفق \n الوقت ↞ {seconds} \n تم اضافه (`{p}`) \n `{a}` لفلوسك')
        add_points(user_id, gid, points, amount=p)
        answer = None
        start_time = None
    elif elapsed_time >= 10:
        is_on = False
        answer = None
        start_time = None
        if a == 5:
            is_on = False
            points_list = "\n".join([f"{pid} -> {info['score']} نقطة" for pid, info in res.items()])
            await event.reply(f"**ترتيب اللاعبين بالنقاط**\n{points_list}")
            is_on = False
@ABH.on(events.NewMessage(func=lambda event: event.text in ['كتويت']))
async def send_random_question(event):
    if not event.is_group:
        return
    type = "كتويت"
    await botuse(type)
    random_question = random.choice(questions)
    await event.reply(random_question)
g = {}
active_players = {}
running_tasks = set()
def format_duration(duration: timedelta) -> str:
    minutes, seconds = divmod(int(duration.total_seconds()), 60)
    return f"{minutes} دقيقة و {seconds} ثانية"
def reset_game(chat_id):
    if chat_id in g:
        del g[chat_id]
    if chat_id in active_players:
        del active_players[chat_id]
    running_tasks.discard(chat_id)
@ABH.on(events.NewMessage(pattern=r'^/(vagueness)$|^غموض$'))
async def vagueness_start(event):
    if not event.is_group:
        return
    type = "غموض"
    await botuse(type)
    chat_id = event.chat_id
    g[chat_id] = {
        "players": set(),
        "player_times": {},
        "game_started": True,
        "join_enabled": True
    }
    active_players[chat_id] = set()
    await event.respond(' تم بدء لعبة الغموض، يسجل اللاعبون عبر أمر `انا`')
@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    user_id = event.sender_id
    game = g.get(chat_id)
    if not game or not game["game_started"] or not game["join_enabled"]:
        return
    if user_id in game["players"]:
        await event.respond('اسمك موجود بالفعل في اللعبة.')
        return
    g["players"].add(user_id)
    g["player_times"][user_id] = {"start": datetime.utcnow()}
    await event.respond('تم تسجيلك، انتظر بدء اللعبة.')
@ABH.on(events.NewMessage(pattern=r'^تم$'))
async def start_game(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    game = g.get(chat_id)
    if not g or not g["game_started"]:
        return
    if len(game["players"]) < 2:
        await event.respond('عدد اللاعبين غير كافٍ لبدء اللعبة.')
        reset_game(chat_id)
        return
    game["join_enabled"] = False
    await event.respond('تم بدء اللعبة , اي رد على رسالة سيؤدي لخسارة اللاعب.')
@ABH.on(events.NewMessage(pattern=r'^الاعبين$'))
async def show_players(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    game = g.get(chat_id)
    if not game or not game["players"]:
        return
    mentions = []
    for uid in game["players"]:
        user = await ABH.get_entity(uid)
        mentions.append(f"[{user.first_name}](tg://user?id={uid})")
    await event.respond("👥 اللاعبون المسجلون\n" + "\n".join(mentions), parse_mode='md')
@ABH.on(events.NewMessage(incoming=True))
async def monitor_messages(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    sender_id = event.sender_id
    game = g.get(chat_id)
    if not game:
        return
    if sender_id in game["players"]:
        if chat_id not in active_players:
            active_players[chat_id] = set()
        active_players[chat_id].add(sender_id)
    if chat_id not in running_tasks:
        running_tasks.add(chat_id)
        asyncio.create_task(track_inactive_players(chat_id))
    reply = await event.get_reply_message()
    if sender_id in game["players"] and reply:
        now = datetime.utcnow()
        start_time = game["player_times"][sender_id]["start"]
        duration = now - start_time
        mention = f"[{(await ABH.get_entity(sender_id)).first_name}](tg://user?id={sender_id})"
        game["players"].remove(sender_id)
        game["player_times"].pop(sender_id, None)
        x = random.randint(500, 1000)
        await event.reply(
            f' اللاعب {mention} رد على رسالة وخسر!\n مدة اللعب {format_duration(duration)} اضفت اله {x}',
            parse_mode='md'
        )
        add_points(sender_id, chat_id, points, amount=x)
        if len(game["players"]) == 1:
            await announce_winner(chat_id)
async def track_inactive_players(chat_id):
    while chat_id in g and g[chat_id]["game_started"]:
        await asyncio.sleep(600)
        game = g.get(chat_id)
        if not game:
            break
        current_players = game["players"].copy()
        current_active = active_players.get(chat_id, set())
        inactive_players = current_players - current_active
        for uid in inactive_players:
            game["players"].discard(uid)
            game["player_times"].pop(uid, None)
            user = await ABH.get_entity(uid)
            await ABH.send_message(
                chat_id,
                f' تم طرد اللاعب [{user.first_name}](tg://user?id={uid}) بسبب عدم التفاعل.',
                parse_mode='md'
            )
        active_players[chat_id] = set()
        if len(game["players"]) == 1:
            await announce_winner(chat_id)
            break
    running_tasks.discard(chat_id)
async def announce_winner(chat_id):
    game = g.get(chat_id)
    if not game or len(game["players"]) != 1:
        return
    winner_id = next(iter(game["players"]))
    winner = await ABH.get_entity(winner_id)
    win_time = datetime.utcnow() - game["player_times"][winner_id]["start"]
    x = random.randint(1000, 10000)
    await ABH.send_message(
        chat_id,
        f'🎉 انتهت اللعبة.\n🏆 الفائز هو: [{winner.first_name}](tg://user?id={winner_id})\n⏱️ مدة اللعب: {format_duration(win_time)} اضف له {x}',
        parse_mode='md'
    )
    add_points(winner_id, chat_id, points, amount=x)
    reset_game(chat_id)
