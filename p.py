import os
import streamlink
from telethon import TelegramClient, events
from telethon.tl.custom import Button

# إعدادات API و BOT
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# دالة لتنزيل الفيديو باستخدام streamlink
async def download_video(url: str):
    try:
        # الحصول على أفضل بث (video stream) من الرابط
        streams = streamlink.streams(url)
        best_stream = streams.get("best")

        # اسم الملف الذي سيتم تنزيل الفيديو فيه
        output_file = 'video.mp4'

        # كتابة الفيديو إلى الملف
        with open(output_file, 'wb') as f:
            for chunk in best_stream.iter_chunks():
                f.write(chunk)
        
        # التحقق من أن الفيديو تم تنزيله
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return output_file
        else:
            return None
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# دالة لمعالجة الرسائل الجديدة
@ABH.on(events.NewMessage(pattern='فديو|فيديو'))
async def handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    query = msg_parts[1]
    
    # تنزيل الفيديو بناءً على الرابط أو الاستعلام
    video_file = await download_video(query)
    
    if video_file:
        # إضافة زر في الرسالة بعد تنزيل الفيديو
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            video_file, 
            caption='**[Enjoy dear]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(video_file)  # إزالة الملف بعد إرساله
    else:
        await event.respond("فشل تحميل الفيديو. تحقق من الرابط أو استعلم عن سبب المشكلة.")

# تشغيل البوت
ABH.run_until_disconnected()
