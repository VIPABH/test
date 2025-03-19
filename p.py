import random, os
from telethon import TelegramClient, events
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
group_game_status = {}
number2 = None
game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
numbers_board = [["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]]
original_game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
points = {}
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
@ABH.on(events.NewMessage(pattern='/rings'))
async def handle_start_game(event):
    global number2
    chat_id = event.chat_id
    user_id = event.sender_id
    username = event.sender.username or "unknown"
    if chat_id not in group_game_status:
        group_game_status[chat_id] = {'game_active': False, 'active_player_id': None}    
    if not group_game_status[chat_id]['game_active']:
        group_game_status[chat_id]['game_active'] = True
        group_game_status[chat_id]['active_player_id'] = user_id
        number2 = random.randint(1, 6)
        group_game_status[chat_id]['number2'] = number2
        await event.respond(
            f"عزيزي [{event.sender.first_name}](https://t.me/@{username})! تم تسجيلك في لعبة محيبس \nارسل `جيب ` + رقم للحزر \n ارسل `طك ` + رقم للتخمين.",
            parse_mode="Markdown"
        )
@ABH.on(events.NewMessage(pattern=r'جيب (\d+)'))
async def handle_guess(event):
    global number2, game_board, points, group_game_status
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            guess = int(event.text.split()[1])  
            if 1 <= guess <= 6:  
                if guess == number2:
                    winner_id = event.sender_id 
                    points[winner_id] = points.get(winner_id, 0) + 1 
                    sender_first_name = event.sender.first_name
                    game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                    await event.reply(f'🎉 الف مبروك! اللاعب ({sender_first_name}) وجد المحبس 💍!\n{format_board(game_board, numbers_board)}')
                    reset_game(chat_id)
                else: 
                    sender_first_name = event.sender.first_name
                    game_board = [["❌" if i == guess - 1 else "🖐️" for i in range(6)]]
                    await event.reply(f"ضاع البات ماضن بعد تلگونة ☹️ \n{format_board(game_board, numbers_board)}")
                    reset_game(chat_id)
            else:
                await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
        except (IndexError, ValueError):
            await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
@ABH.on(events.NewMessage(pattern=r'طك (\d+)'))
async def handle_strike(event):
    global game_board, number2, group_game_status
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            strike_position = int(event.text.split()[1])  
            if strike_position == number2:
                game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                await event.reply(f"**خسرت!** \n{format_board(game_board, numbers_board)}")
                reset_game(chat_id)

                abh = [
                    "تلعب وخوش تلعب 👏🏻",
                    "لك عاش يابطل استمر 💪🏻",
                    "على كيفك ركزززز انتَ كدها 🤨",
                    "لك وعلي ذيييب 😍"
                ]
                iuABH = random.choice(abh)
                game_board[0][strike_position - 1] = '🖐️'
                await event.reply(f" {iuABH} \n{format_board(game_board, numbers_board)}")
            elif strike_position != number2:
                await event.reply('خطا')
        except (IndexError, ValueError):
            await event.reply("يرجى إدخال رقم صحيح بين 1 و 6.")
            
@ABH.on(events.NewMessage(pattern='/محيبس'))
async def show_number(event):
    """إظهار الرقم السري عند الطلب وإرساله إلى @k_4x1"""
    chat_id = event.chat_id
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        target_user_id = 1910015590  
        await ABH.send_message(target_user_id, f"الرقم السري هو: {number2}")
        await event.reply("تم إرسال الرقم السري إلى @k_4x1.")
    else:
        await event.reply("لم تبدأ اللعبة بعد. أرسل /rings لبدء اللعبة.")
ABH.run_until_disconnected()
