from helpers import *
import os

bot = os.getenv("BOT_TOKEN")




myus = ""




def myChannelButton(username:str=None):
    if username:
        ch = bot.get_chat(username)
        username = username.replace("@", "")
        return InlineKeyboardButton(text=ch.title, url=f"https://t.me/{username}")


@bot.message_handler(func=lambda message: message.text.startswith(("يوت ", "يوتيوب ")))
def handle_youtube_search(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    search_query = re.sub(r"^(يوت|يوتيوب)\s+", "", message.text, count=1).strip()
    ddtyt = yUtube_data(user_id, chat_id)
    ddtyt.delfile(f"{message.from_user.id}_{message.chat.id}.json")
    data = ddtyt.word2links(message, search_query)
    markup = ddtyt.generate_markup(data, 'yt_close', message)
    if myus:
        btn = myChannelButton(myus)
        markup.add(btn)
    bot.send_message(message.chat.id, text='____', reply_markup=markup)
    ddtyt.set_value("fmsg", message.id)
    ddtyt.set_value("ftime", datetime.now())
    ddtyt.deldata("ftime")


@bot.callback_query_handler(func=lambda call : True)
def quhndr(call:telebot.types.CallbackQuery):
    data = call.data
    data = call.data
    msg = call.message

    chat_id = msg.chat.id
    msg_id = msg.id
    user_id = call.from_user.id
    ddtyt = yUtube_data(user_id, chat_id)
    FILENAME = f"{call.from_user.id}_{msg.chat.id}.json"
    if "YT" in data:
        extracted_data  = ddtyt.extract_data_yt(data, 'YT')
        ID = extracted_data['id']
        userID = extracted_data['user_id']
        chatID = extracted_data['chat_id']
        if userID == user_id and chatID == chat_id: 
            my_data = ddtyt.view_items(FILENAME)
            for i_d in my_data:
                if i_d['id'] == ID:
                    mrkup = ddtyt.select_type_mrkup_yt(ID, call)
                    if myus:
                        btn = myChannelButton(myus)
                        mrkup.add(btn)
                    # caption = f"{i_d['title']} \n[duration = {i_d['duration']}]\n`"
                    caption = ddtyt.detxt(i_d['title'], i_d['duration'])
                    bot.delete_message(chat_id, msg_id)
                    send_data = {
                        "chat_id": chat_id,
                        "caption": caption,
                        "reply_markup": mrkup,
                        "photo": i_d['thumbnails'][-1],
                        # "reply_to_message_id": msg_id
                        "parse_mode": 'html',
                    }
                    m = bot.send_photo(**send_data)
                    ddtyt.set_value("mmsg", m.id)
                    ddtyt.set_value("mtime", datetime.now())
                    ddtyt.deldata("mtime")
                    return

    elif "vidyt" in data:
        extracted_data  = ddtyt.extract_data_yt(data, "vidyt")
        ID = extracted_data['id']
        userID = extracted_data['user_id']
        chatID = extracted_data['chat_id']
        if userID == user_id and chatID == chat_id: 
            downloadingtext = "تم التحميل ارجاء الانتظار\n"
            senddingtext = "يتم الارسال الرجاء الانتظار \n"
            m = bot.send_message(chat_id, downloadingtext+ ddtyt.step_text*2)
            my_data = ddtyt.view_items(FILENAME)
            m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= downloadingtext+ ddtyt.step_text*4)
            for i_d in my_data:
                if i_d['id'] == ID:
                    mrkup = None
                    if myus:
                        mrkup = InlineKeyboardMarkup()
                        btn = myChannelButton(myus)
                        mrkup.add(btn)
                    bot.send_chat_action(chat_id, "upload_video")
                    file_name = f"{user_id}_{chat_id}_{ID}"
                    bot.delete_message(chat_id, msg_id)
                    m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= downloadingtext+ ddtyt.step_text*6)
                    media = ddtyt.get_yt_link_by_id('video', ID, file_name)
                    m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= downloadingtext+ ddtyt.step_text*7)
                    # caption = f"""<b>{i_d['title']} \nالمدة 🥟: = {i_d['duration']}\nُ </b>"""
                    caption = ddtyt.detxt(i_d['title'], i_d['duration'])
                    bot.send_chat_action(chat_id, "upload_video")
                    try:
                        m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= senddingtext)
                        with open(media, 'rb') as file:
                            send_data = {
                                "thumbnail": None,
                                "chat_id": chat_id,
                                # "width": 120,
                                # "height": 150,
                                "caption": caption,
                                "reply_markup": mrkup,
                                "video": file, # if media if file
                                "reply_to_message_id": ddtyt.get_value('fmsg'),
                                "parse_mode": 'html',
                            }
                            bot.send_video(**send_data, timeout=100)
                            try:
                                bot.delete_message(chat_id, m.id)
                            except:
                                ...
                            file.close()
                    except:
                        ...
                    ddtyt.delfile(FILENAME)
                    ddtyt.del_user()
                    ddtyt.delfile(media)

    elif "audyt" in data:
        extracted_data  = ddtyt.extract_data_yt(data, "audyt")
        ID = extracted_data['id']
        userID = extracted_data['user_id']
        chatID = extracted_data['chat_id']
        if userID == user_id and chatID == chat_id:
            downloadingtext = "تم التحميل ارجاء الانتظار\n"
            senddingtext = "يتم الارسال الرجاء الانتظار \n"
            m = bot.send_message(chat_id, downloadingtext+ ddtyt.step_text*2)
            my_data = ddtyt.view_items(FILENAME)
            m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= downloadingtext+ ddtyt.step_text*4)
            for i_d in my_data:
                if i_d['id'] == ID:
                    mrkup = None
                    if myus:
                        mrkup = InlineKeyboardMarkup()
                        btn = myChannelButton(myus)
                        mrkup.add(btn)
                    file_name = f"{user_id}_{chat_id}_{ID}".replace("-", "_")
                    bot.delete_message(chat_id, msg_id)
                    bot.send_chat_action(chat_id, "upload_voice")
                    m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= downloadingtext+ ddtyt.step_text*6)
                    media = ddtyt.get_yt_link_by_id('audio', ID, file_name)
                    m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= senddingtext+ ddtyt.step_text*7)
                    # media = ur2_yt_url(ID, 'a')
                    
                    # caption = f"""<b>{i_d['title']} \nالمدة 🥟: = {i_d['duration']}\nُ </b>"""
                    caption = ddtyt.detxt(i_d['title'], i_d['duration'])
                    bot.send_chat_action(chat_id, "upload_voice")
                    try:
                        m = bot.edit_message_text(chat_id=chat_id,message_id=m.id, text= senddingtext)
                        with open(media, 'rb') as file:
                            send_data = {
                                "chat_id": chat_id,
                                "thumbnail": requests.get(i_d['thumbnails'][-1]).content,
                                "title": i_d['title'][:10],
                                "performer": i_d['channel'][:10],
                                "caption": caption,
                                "reply_markup": mrkup,
                                "audio": file, # if media if file
                                # "audio": media, # if media if url
                                "reply_to_message_id": ddtyt.get_value('fmsg'),
                                "parse_mode": 'html',
                            }
                            try:
                                bot.send_audio(**send_data)
                                try:
                                    bot.delete_message(chat_id, m.id)
                                except:
                                    ...
                            except:
                                del send_data['reply_to_message_id']
                            file.close()
                    except:
                        ...
                    ddtyt.delfile(FILENAME)
                    ddtyt.delfile(media)
                    ddtyt.del_user()                
                    return

    elif data == "yt_close": 
        try:
            bot.delete_message(chat_id, msg.id)
        except:
            ...    
        try:
            bot.delete_message(chat_id, ddtyt.get_value('fmsg'))
        except:
            ...
        ddtyt.delfile(FILENAME)
        ddtyt.del_user()  





bot.infinity_polling(skip_pending=True)
