import logging
import os
import requests
import re
from telethon import events, TelegramClient
from youtubesearchpython import VideosSearch

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

AUDIO_API = "https://api.vevioz.com/api/button/mp3/"

@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def yt_search(event):
    query = event.pattern_match.group(2)
    await event.reply("🔍 جاري البحث عن الأغنية...")

    try:
        # لو كتب رابط مباشر
        if "youtube.com/watch" in query or "youtu.be/" in query:
            video_link = query
            title = "الصوت المطلوب"
        else:
            # بحث عن الكلمة
            videos_search = VideosSearch(query, limit=1)
            result = videos_search.result()['result']

            if not result:
                await event.reply("❗️ لم يتم العثور على نتائج.")
                return
            
            video_link = result[0]['link']
            title = result[0]['title']

        await event.reply(f"🎶 تم العثور على:\n{title}\n\n⏳ جاري تحميل الصوت...")

        # استخراج ID الفيديو
        if "v=" in video_link:
            video_id = video_link.split('v=')[-1]
        else:
            video_id = video_link.split('/')[-1]

        response = requests.get(AUDIO_API + video_id, timeout=30)
        if response.status_code != 200:
            await event.reply("❗️ تعذر الوصول لرابط التحميل.")
            return
        
        mp3_links = re.findall(r'href="(https://vevioz\.com/dl/.+?)"', response.text)
        if not mp3_links:
            await event.reply("❗️ لم أجد رابط تحميل للصوت.")
            return
        
        mp3_link = mp3_links[0]

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        temp_path = f"downloads/{safe_title}.mp3"

        try:
            audio_content = requests.get(mp3_link, timeout=60).content
            with open(temp_path, 'wb') as f:
                f.write(audio_content)

            if os.path.getsize(temp_path) > 50 * 1024 * 1024:
                await event.reply("⚠️ الملف أكبر من 50 ميغابايت، لا يمكن إرساله.")
                os.remove(temp_path)
                return

            await event.client.send_file(
                event.chat_id,
                temp_path,
                caption=f"🎵 {title}",
                voice_note=False,
                reply_to=event.message.id
            )

            await event.reply("✅ تم الإرسال بنجاح!")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logging.error(f"خطأ بالبحث أو التحميل: {e}")
        await event.reply("❗️ حصل خطأ مفاجئ. حاول مرة ثانية.")

print("✅ البوت يعمل الآن...")
ABH.run_until_disconnected()
