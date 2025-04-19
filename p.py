import requests
import yt_dlp, os
import telebot
from io import BytesIO

TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')
API_KEY = 'AIzaSyDUicHGozWPYq-aUxcCYdKbmqk5Mj_IaXg'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'] and any(key.lower() in message.text.lower() for key in ['yt', 'يوت', 'UT']))
def search_and_download_audio(message):
    search_query = message.text.lower()
    for key in ['yt', 'يوت', 'ut']:
        if key in search_query:
            search_query = search_query.replace(key, '', 1).strip()
            break

    msg = bot.send_message(message.chat.id, "جاري التحميل ...", reply_to_message_id=message.message_id)

    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&key={API_KEY}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()

        data = response.json()
        if 'items' in data:
            video_id = data['items'][0]['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'outtmpl': '-',
                'extractaudio': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                audio_url = info_dict.get("url", None)

                if audio_url:
                    audio_data = requests.get(audio_url).content
                    audio_file = BytesIO(audio_data)
                    title = info_dict.get('title', 'Untitled')
                    audio_file.name = f"{title}.mp3"
                    bot.delete_message(message.chat.id, msg.message_id)
                    bot.send_audio(message.chat.id, audio_file, caption=f"تم التحميل ✓: {title}", reply_to_message_id=message.message_id)
                else:
                    bot.delete_message(message.chat.id, msg.message_id)
                    bot.send_message(message.chat.id, "فشل تحميل الصوت.")
        else:
            bot.delete_message(message.chat.id, msg.message_id)
            bot.send_message(message.chat.id, "لم أتمكن من العثور على الفيديو.")
    
    except requests.exceptions.RequestException as e:
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, f"حدث خطأ أثناء التواصل مع YouTube API: {e}")
print('done')
bot.polling(none_stop=True)
