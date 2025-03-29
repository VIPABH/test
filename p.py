from pytube import YouTube
import os
from telethon import events
from telethon.tl.custom import Button
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
async def download_video(query: str):
    try:
        # إذا لم يكن الرابط موجودًا، يتم تحويل النص إلى رابط بحث يوتيوب
        if not query.startswith(("http://", "https://")):
            query = f"https://www.youtube.com/results?search_query={query}"
        
        # تحميل الفيديو
        yt = YouTube(query)
        video_stream = yt.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
        
        # تحديد اسم الملف
        output_file = f"{yt.title}.mp4"
        
        # تنزيل الفيديو إلى الملف المحلي
        video_stream.download(filename=output_file)
        
        # التأكد من أن الفيديو تم تنزيله بنجاح
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return output_file
        else:
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# الدالة لمعالجة الرسائل الجديدة
@ABH.on(events.NewMessage(pattern='فديو|فيديو'))
async def handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    query = msg_parts[1]
    
    # تحميل الفيديو بناءً على الاستعلام
    video_file = await download_video(query)
    
    if video_file:
        # إضافة زر في الرسالة بعد تحميل الفيديو
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
ABH.run_until_disconnected()
