from youtube_search import YoutubeSearch
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import os, json, re, requests, yt_dlp, telebot, ast



# لتلعب بيها 
my_users_on_yt= {}
# خليها كما هي



class yUtube_data:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.key = f"{user_id}_{chat_id}"
    def set_value(self, nkey, nvalue):
        if self.key not in my_users_on_yt:
            my_users_on_yt.update(
                {
                    self.key: {
                        nkey: nvalue
                    }
                }
            )
            return
        my_users_on_yt[self.key][nkey] = nvalue 

    def del_value(self, nkey):
        if self.key in my_users_on_yt:
            del my_users_on_yt[self.key][nkey]

    def get_user(self):
        return my_users_on_yt.get(self.key)

    def get_value(self, nkey):
        if self.key in my_users_on_yt:
            return my_users_on_yt[self.key].get(nkey)

    def del_user(self):
        if self.key in my_users_on_yt:
            del my_users_on_yt[self.key]

    def deldata(self, ttype):
        for key in my_users_on_yt:
            FILENAME = f"{key}.json"
            t = my_users_on_yt[key].get(ttype)
            if self.minutes_passed(t):
                self.delfile(FILENAME)
                user_id, chat_id = self.extract_ids(key)
                self.del_user(user_id, chat_id)
                self.delfile(FILENAME)

    def delfile(self, file_name):
        try:
            os.remove(file_name)
        except:
            ...

    def minutes_passed(self, stime):
        try:
            return datetime.now() - stime >= timedelta(minutes=15)
        except:
            ...


    def view_items(self, FILENAME):
        with open(FILENAME, "r") as file:
            data = json.load(file)
        return data  

    def create_box_data_ytUSER(self, msg, data:list):
        FILENAME = f"{msg.from_user.id}_{msg.chat.id}.json"
        self.delfile(FILENAME)
        if not os.path.exists(FILENAME):
            with open(FILENAME, "w") as file:
                json.dump(data, file)  
                file.close()

    def word2links(self, msg, word:str, max_results=5):
        """    
        ### thumbnails
        ### id
        ### title
        ### duration
        ### channel
        ### views
        ### publish_time
        """
        data = YoutubeSearch(word, max_results=max_results).to_dict()
        self.create_box_data_ytUSER(msg, data)
        return data

    def extract_ids(self, text):
        match = re.search(r'(\d+)_(\d+)', text)
        if match:
            user_id, chat_id = match.groups()
            return int(user_id), int(chat_id)
        return None, None

    def extract_data_yt(self, call_data:str, t):
        call_data  = call_data.lstrip(t)
        list_data = ast.literal_eval(call_data.replace("[", "['").replace(", ", "', '").replace("]", "']"))

        # match = re.match(fr'{re.escape(t)}\[(.*?), (\d+), (\d+)\]', call_data.strip())
        # if match:
        #     video_id, chat_id, user_id = match.groups()
        return {
            "id": list_data[0],
            "chat_id": int(list_data[1]),
            "user_id": int(list_data[2])
        }
        
    def get_yt_link_by_id(self, type_yt, vid, file_name):
        url = f"https://youtu.be/{vid}"
        is_audio = type_yt != "video"

        options = {
            'format': 'bestaudio/best' if is_audio else 'best',
            'quiet': True,
            'noplaylist': True,
            'outtmpl': f'{file_name}.%(ext)s',
        }

        if is_audio:
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                return f"{file_name}.mp3" if is_audio else f"{file_name}.{info['ext']}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    @property
    def step_text(self):
        return '🎤🎤🎤'


    def generate_markup(self, data, close_name, msg):
        mrkup = InlineKeyboardMarkup()
        for d in data:
            mrkup.add(
                InlineKeyboardButton(text=d['title'], callback_data=f'YT[{d["id"]}, {msg.chat.id}, {msg.from_user.id}]')
            )
        mrkup.add(InlineKeyboardButton(text=". اغلاق .", callback_data=close_name))
        # btn = myChannelButton(myus)
        # mrkup.add(btn)
        return mrkup

    def select_type_mrkup_yt(self, vid, call):
        msg = call.message
        mrkup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text='. فيديو .', callback_data=f'vidyt[{vid}, {msg.chat.id}, {call.from_user.id}]'),
                    InlineKeyboardButton(text='. اوديو .', callback_data=f'audyt[{vid}, {msg.chat.id}, {call.from_user.id}]'),
                ],
                [
                    InlineKeyboardButton(text='. اغلاق .', callback_data=f'yt_close'),
                ],
            ]
        )

        return mrkup






    def detxt(self, title, ti):
        v = f"""<b> {title}

    المدة 🕑 : <code>{ti}</code>
    ‘
    </b>"""
        return v
