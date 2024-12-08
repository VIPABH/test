import random
import telebot
from telebot import types

# استبدل هذا بالـ token الخاص بك
bot = telebot.TeleBot("7273443857:AAFt8PtcI_gdYp0QbtcJH1Tu1oFJn9-H0yk")

# متغيرات اللعبة
game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
numbers_board = [["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]]
original_game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
joker = ["🤔", "🙄", "😳", "🥲", "😜"]
correct_answer = None  
group_game_status = {}
points = {}

def format_board(game_board, numbers_board):
    """تنسيق الجدول للعرض بشكل مناسب"""
    formatted_board = ""
    formatted_board += " ".join(numbers_board[0]) + "\n"
    formatted_board += " ".join(game_board[0]) + "\n"
    return formatted_board

def reset_game(chat_id):
    """إعادة تعيين حالة اللعبة بعد انتهائها"""
    global game_board, correct_answer, group_game_status
    game_board = [row[:] for row in original_game_board]
    correct_answer = None
    group_game_status[chat_id]['is_game_started2'] = False
    group_game_status[chat_id]['joker_player'] = None

@bot.message_handler(func=lambda message: message.text == 'محيبس')
def start_game(message):
    """بدء اللعبة عند الضغط على زر 'محيبس'"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ابدأ اللعبة", callback_data="start_game"))

    username = message.from_user.username or "unknown"
    bot.send_video(
        message.chat.id,
        "t.me/VIPABH/1210",  
        caption=f"أهلاً [{message.from_user.first_name}](https://t.me/{username})! حياك الله. اضغط على الزر لبدء اللعبة.",
        parse_mode="Markdown",
        reply_markup=markup
    ) 

    chat_id = message.chat.id
    if chat_id not in group_game_status:
        group_game_status[chat_id] = {'is_game_started2': False, 'joker_player': None}

    if not group_game_status[chat_id]['is_game_started2']:
        group_game_status[chat_id]['is_game_started2'] = True
        group_game_status[chat_id]['joker_player'] = None
        correct_answer = random.randint(1, 6)  # تعيين الرقم السري عند بدء اللعبة

@bot.message_handler(regexp=r'\طك (\d+)')
def handle_strike(message):
    """التعامل مع ضربات اللاعبين لاختيار الرقم"""
    global game_board, correct_answer, group_game_status

    chat_id = message.chat.id
    if chat_id in group_game_status and group_game_status[chat_id]['is_game_started2']:
        try:
            strike_position = int(message.text.split()[1])
            if strike_position == correct_answer:
                # إذا كانت الإجابة صحيحة
                game_board = [["💍" if i == correct_answer - 1 else "🖐️" for i in range(6)]]
                bot.reply_to(message, f"**خسرت! المحبس كان هنا.**\n{format_board(game_board, numbers_board)}")
                reset_game(chat_id)  # إعادة تعيين اللعبة
            else:
                # إذا كانت الإجابة خاطئة
                game_board[0][strike_position - 1] = '🖐️'
                lMl10l = random.choice(joker)
                bot.reply_to(message, f"**{lMl10l}**\n{format_board(game_board, numbers_board)}")
        except (IndexError, ValueError):
            bot.reply_to(message, "❗ يرجى إدخال رقم صحيح بين 1 و 6.")

@bot.message_handler(regexp=r'\جيب (\d+)')
def handle_guess(message):
    """التعامل مع التخمينات من قبل اللاعبين"""
    global group_game_status, correct_answer, game_board, points

    chat_id = message.chat.id
    if chat_id in group_game_status and group_game_status[chat_id]['is_game_started2']:
        try:
            guess = int(message.text.split()[1])
            if 1 <= guess <= 6:
                if guess == correct_answer:
                    # إذا كان التخمين صحيحًا
                    winner_id = message.from_user.id
                    points[winner_id] = points.get(winner_id, 0) + 1
                    sender_first_name = message.from_user.first_name
                    game_board = [["💍" if i == correct_answer - 1 else "🖐️" for i in range(6)]]
                    bot.send_message(chat_id, f'🎉 الف مبروك! اللاعب ({sender_first_name}) وجد المحبس 💍!\n{format_board(game_board, numbers_board)}')
                    reset_game(chat_id)  # إعادة تعيين اللعبة
                else:
                    # إذا كان التخمين خاطئًا
                    sender_first_name = message.from_user.first_name
                    game_board = [["❌" if i == guess - 1 else "🖐️" for i in range(6)]]
                    bot.send_message(chat_id, f"❌ اللاعب ({sender_first_name}) خسر اللعبة! المحبس لم يكن هنا.\n{format_board(game_board, numbers_board)}")
                    reset_game(chat_id)  # إعادة تعيين اللعبة
            else:
                bot.reply_to(message, "❗ يرجى إدخال رقم صحيح بين 1 و 6.")
        except (IndexError, ValueError):
            bot.reply_to(message, "❗ يرجى إدخال رقم صحيح بين 1 و 6.")

# بدء البوت
bot.polling()
