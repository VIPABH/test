import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading 
import random
import time
import os
bot_token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)

def delete_after_delay99(chat_id, message_id, delay=30):
    threading.Timer(delay, lambda: bot.delete_message(chat_id, message_id)).start()

group_game_status = {}
number2 = None
game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
numbers_board = [["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]]
original_game_board = [["👊", "👊", "👊", "👊", "👊", "👊"]]
points = {}

def format_board(game_board, numbers_board):
    """تنسيق الجدول للعرض بشكل مناسب"""
    formatted_board = ""
    formatted_board += " ".join(numbers_board[0]) + "\n"
    formatted_board += " ".join(game_board[0]) + "\n"
    return formatted_board

def reset_game(chat_id):
    """إعادة تعيين حالة اللعبة بعد انتهائها"""
    global game_board, number2, group_game_status
    game_board = [row[:] for row in original_game_board]
    number2 = None
    
    group_game_status[chat_id]['game_active'] = False
    group_game_status[chat_id]['active_player_id'] = None
@bot.message_handler(func=lambda message: message.text == 'محيبس')
def start_game(message):
    global number2
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ابدأ اللعبة", callback_data="startGame"))

    username = message.from_user.username or "unknown"
    sent_msg = bot.send_video(
        message.chat.id,
        "t.me/VIPABH/1210",  
        caption=f"أهلاً [{message.from_user.first_name}](https://t.me/{username})! حياك الله. اضغط على الزر لبدء اللعبة.",
        parse_mode="Markdown",
        reply_markup=markup
    )

    threading.Thread(target=delete_message_after1, args=(message.chat.id, sent_msg.message_id)).start()

def delete_message_after1(chat_id, message_id, delay=3):
    """حذف الرسالة بعد مهلة زمنية محددة"""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"حدث خطأ أثناء حذف الرسالة: {e}")

    if chat_id not in group_game_status:
        
        group_game_status[chat_id] = {'game_active': False, 'active_player_id': None}

@bot.callback_query_handler(func=lambda call: call.data == "startGame")
def handle_start_game(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if chat_id not in group_game_status:
        
        group_game_status[chat_id] = {'game_active': False, 'active_player_id': None}


    if not group_game_status[chat_id]['game_active']:
        
        group_game_status[chat_id]['game_active'] = True
        group_game_status[chat_id]['active_player_id'] = user_id

        global number2
        number2 = random.randint(1, 6)
        group_game_status[chat_id]['number2'] = number2
        
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None 
        )
        
        sent_msg2 = bot.send_message(
            chat_id,
            "تم تسجيلك في لعبة محيبس \n ملاحظة: لفتح العضمة ارسل طك ورقم العضمة لأخذ المحبس أرسل جيب ورقم العضمة."
        )
        
        threading.Thread(target=delete_message_after10, args=(chat_id, sent_msg2.message_id)).start()

def delete_message_after10(chat_id, message_id, delay=3):
    """حذف الرسالة بعد مهلة زمنية محددة"""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"حدث خطأ أثناء حذف الرسالة: {e}")
@bot.message_handler(regexp=r'جيب (\d+)')
def handle_guess(message):
    global number2, game_board, points, group_game_status

    chat_id = message.chat.id
    
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            guess = int(message.text.split()[1])
            if 1 <= guess <= 6:
                if guess == number2:
                    winner_id = message.from_user.id
                    points[winner_id] = points.get(winner_id, 0) + 1
                    sender_first_name = message.from_user.first_name
                    game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                    sent_msg3 = bot.reply_to(message, f'🎉 الف مبروك! اللاعب ({sender_first_name}) وجد المحبس 💍!\n{format_board(game_board, numbers_board)}')
                    threading.Thread(target=delete_message_after2, args=(message.chat.id, sent_msg3.message_id)).start()

                    def delete_message_after2(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
                            
                    reset_game(chat_id)
                else:
                    sender_first_name = message.from_user.first_name
                    game_board = [["❌" if i == guess - 1 else "🖐️" for i in range(6)]]
                    sent_msg4 = bot.reply_to(message, f"ضاع البات ماضن بعد تلگونة ☹️ \n{format_board(game_board, numbers_board)}")
                    threading.Thread(target=delete_message_after3, args=(message.chat.id, sent_msg4.message_id)).start()

                    def delete_message_after3(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
                    reset_game(chat_id)
            else:
                sent_msg5 = bot.reply_to(message, "❗ يرجى إدخال رقم صحيح بين 1 و 6.")
                threading.Thread(target=delete_message_after4, args=(message.chat.id, sent_msg5.message_id)).start()

                def delete_message_after4(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
        except (IndexError, ValueError):
            sent_msg6 = bot.reply_to(message, "❗ يرجى إدخال رقم صحيح بين 1 و 6.")
            threading.Thread(target=delete_message_after5, args=(message.chat.id, sent_msg6.message_id)).start()

            def delete_message_after5(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
@bot.message_handler(regexp=r'\طك (\d+)')
def handle_strike(message):
    global game_board, number2, group_game_status

    chat_id = message.chat.id
    
    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        try:
            strike_position = int(message.text.split()[1])
            if strike_position == number2:
                game_board = [["💍" if i == number2 - 1 else "🖐️" for i in range(6)]]
                
                bot.reply_to(message, f"**خسرت!** \n{format_board(game_board, numbers_board)}")
                reset_game(chat_id) 
            else:
                abh = [
    "تلعب وخوش تلعب 👏🏻",
    "لك عاش يابطل استمر 💪🏻",
    "على كيفك ركزززز انتَ كدها 🤨",
    "لك وعلي ذيييب 😍"]
                
                iuABH = random.choice(abh)

                game_board[0][strike_position - 1] = '🖐️'
                sent_msg7 = bot.reply_to(message, f" {iuABH} \n{format_board(game_board, numbers_board)}")
                threading.Thread(target=delete_message_after6, args=(message.chat.id, sent_msg7.message_id)).start()

                def delete_message_after6(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
        except (IndexError, ValueError):
            sent_msg8 = bot.reply_to(message, "يرجى إدخال رقم صحيح بين 1 و 6.")
            threading.Thread(target=delete_message_after8, args=(message.chat.id, sent_msg8.message_id)).start()

            def delete_message_after7(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")
@bot.message_handler(commands=['محيبس'])
def show_number(message):
    """إظهار الرقم السري عند الطلب وإرساله إلى @k_4x1"""
    chat_id = message.chat.id

    if chat_id in group_game_status and group_game_status[chat_id]['game_active']:
        target_user_id = 1910015590
        
        sent_msg9 = bot.send_message(target_user_id, f"الرقم السري هو: {number2}")
        threading.Thread(target=delete_message_after8, args=(message.chat.id, sent_msg9.message_id)).start()
        def delete_message_after8(chat_id, message_id, delay=3):
            """حذف الرسالة بعد مهلة زمنية محددة"""
            time.sleep(delay)
            try:
                bot.delete_message(chat_id, message_id)
                chat_id = message.chat.id
            except Exception as e:
                print(f"حدث خطأ أثناء حذف الرسالة: {e}")
                sent_msg10 = bot.reply_to(message, "تم إرسال الرقم السري إلى @k_4x1.")
                threading.Thread(target=delete_message_after9, args=(message.chat.id, sent_msg10.message_id)).start()
                def delete_message_after9(chat_id, message_id, delay=3):
                    """حذف الرسالة بعد مهلة زمنية محددة"""
                    time.sleep(delay)
                    try:
                        bot.delete_message(chat_id, message_id)
                        chat_id = message.chat.id
                    except Exception as e:
                        print(f"حدث خطأ أثناء حذف الرسالة: {e}")
    else:
        sent_msg11 = bot.reply_to(message, "لم تبدأ اللعبة بعد. أرسل 'محيبس' لبدء اللعبة.")
        threading.Thread(target=delete_message_after11, args=(message.chat.id, sent_msg11.message_id)).start()
        def delete_message_after11(chat_id, message_id, delay=3):
                        """حذف الرسالة بعد مهلة زمنية محددة"""
                        time.sleep(delay)
                        try:
                            bot.delete_message(chat_id, message_id)
                            chat_id = message.chat.id
                        except Exception as e:
                            print(f"حدث خطأ أثناء حذف الرسالة: {e}")