import yt_dlp
import requests
import telebot
import os
from telebot.types import InputFile

TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')
API_KEY = 'AIzaSyDUicHGozWPYq-aUxcCYdKbmqk5Mj_IaXg'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: any(key.lower() in message.text.lower() for key in ['yt', 'يوت', 'ut']))
def search_and_download_audio(message):
    search_query = message.text.lower()
    for key in ['yt', 'يوت', 'ut']:
        if key in search_query:
            search_query = search_query.replace(key, '', 1).strip()
            break
    bot.reply_to(message, f'تم العثور على البحث: {search_query}')

    msg = bot.send_message(message.chat.id, "جاري التحميل ...", reply_to_message_id=message.message_id)

    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&key={API_KEY}"
    response = requests.get(search_url)
    data = response.json()

    if 'items' in data:
        try:
            for item in data['items']:
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    break
            else:
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_message(message.chat.id, "ماكو فيديو مناسب بهالاسم.")
                return

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'song.%(ext)s',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                title = info_dict.get('title', 'Untitled')
                ext = info_dict.get('ext', 'webm')

            filename = f"song.{ext}"
            audio = InputFile(filename)
            bot.delete_message(message.chat.id, msg.message_id)
            bot.send_audio(message.chat.id, audio, caption=f"تم التحميل ✓: {title}", reply_to_message_id=message.message_id)
            os.remove(filename)

        except Exception as e:
            bot.delete_message(message.chat.id, msg.message_id)
            bot.send_message(message.chat.id, f"حدث خطأ: {e}")
    else:
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, "ما حصلت شي بهالاسم.")

bot.polling(none_stop=True)
