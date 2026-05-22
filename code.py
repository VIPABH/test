import asyncio
import json
import os
import re
import time
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from Resources import lock, hint, wfffp
from ABH import ABH, r

CHANNEL_KEY = 'x04ou'
COOKIES_PATH = 'cookies.txt'
DOWNLOADS_DIR = 'downloads'

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

channel = r.get(CHANNEL_KEY)
if isinstance(channel, bytes):
    channel = channel.decode()

executor = ThreadPoolExecutor(max_workers=60)
download_semaphore = asyncio.Semaphore(20)


# تحديث خيارات yt-dlp لتصبح مرنة مع كافة التنسيقات وتفعيل التحويل التلقائي
YDL_OPTS = {
    "format": "bestaudio[ext=m4a]",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "outtmpl": f"{DOWNLOADS_DIR}/%(id)s.%(ext)s", 
    "cookiefile": COOKIES_PATH,
    "js_runtimes": {"node": {}},
    # إضافة معالج ffmpeg لتحويل أي صيغة غريبة تلقائياً إلى m4a متوافقة مع التليجرام
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "m4a",
        "preferredquality": "192",
    }],
    "extractor_args": {
        "youtube": {
            "client": ["ios", "android"]
        }
    },
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    }
}

def download_audio_sync(url):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        # بما أن المعالج يغير الامتداد دائماً إلى .m4a، نضمن الحصول على المسار الصحيح النهائي للملف
        filename = ydl.prepare_filename(info)
        actual_filename = os.path.splitext(filename)[0] + ".m4a"
        return actual_filename, info



async def fast_upload(client, file_path, **kwargs):
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        return await client.upload_file(
            f, 
            file_name=file_name,
            use_cache=False,
            part_size_kb=1024, 
            **kwargs
        )

async def run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))

def search_yt_sync(query):
    try:
        return Y88F8(query, max_results=1).to_dict()
    except:
        return []

def download_audio_sync(url):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info

async def send_from_cache(event, vid_id, raw_cache, target):
    if isinstance(raw_cache, bytes):
        raw_cache = raw_cache.decode('utf-8')
    try:
        cache = json.loads(raw_cache)
        file = InputDocument(
            id=cache["audio_id"], 
            access_hash=cache["access_hash"], 
            file_reference=bytes.fromhex(cache["file_reference"])
        )
        duration = int(cache.get("duration", 0))
        duration_string = time.strftime('%M:%S', time.gmtime(duration))
        
        await ABH.send_file(
            target, 
            file, 
            reply_to=event.id, 
            caption=f'@{channel} ~ {duration_string} ⏳',
            attributes=[DocumentAttributeAudio(
                duration=duration, 
                title=cache.get("title", "YouTube Audio"), 
                performer=cache.get("performer", "YouTube")
            )]
        )
        return True
    except Exception:
        r.delete(f"ytvideo{vid_id}")
        return False

@ABH.on(events.NewMessage(pattern='^(حمل|يوت|تحميل|yt) ?(.*)'))
async def ytdownloaderHandler(event):
    if not event.is_group:
        return        
    cmd = event.pattern_match.group(1)
    l = lock(event, "يوتيوب")    
    target = event.chat_id
    if cmd != 'حمل' and not l:
        target = r.get('channel_hint')
        if isinstance(target, bytes): 
            target = target.decode()
            
    asyncio.create_task(yt_func(event, target))

async def yt_func(event, target):
    query = event.pattern_match.group(2).strip()
    
    if not query:
        re_msg = await event.get_reply_message()
        if re_msg and re_msg.text: 
            query = re_msg.text
        else: 
            return await event.reply("⚠️ يرجى إرسال اسم الفيديو أو الرابط مع الأمر.")

    query_clean = query.lower().strip()
    vid_id_from_url = None
    
    if "youtube.com/watch?v=" in query:
        vid_id_from_url = query.split("v=")[1].split("&")[0]
    elif "youtu.be/" in query:
        vid_id_from_url = query.split("/")[-1].split("?")[0]
        
    if vid_id_from_url:
        raw_cache = r.get(f"ytvideo{vid_id_from_url}")
        if raw_cache:
            success = await send_from_cache(event, vid_id_from_url, raw_cache, target)
            if success: return
    else:
        cached_id = r.get(f"ytquery:{query_clean}")
        if cached_id:
            if isinstance(cached_id, bytes): 
                cached_id = cached_id.decode()
            raw_cache = r.get(f"ytvideo{cached_id}")
            if raw_cache:
                success = await send_from_cache(event, cached_id, raw_cache, target)
                if success: return

    async with download_semaphore:
        try:
            if vid_id_from_url:
                vid_id = vid_id_from_url
            else:
                results = await run_sync(search_yt_sync, query)
                if not results:
                    return await event.reply("❌ لم يتم العثور على نتائج.")
                vid_id = results[0]["id"]

            raw_cache = r.get(f"ytvideo{vid_id}")
            if raw_cache:
                r.set(f"ytquery:{query_clean}", vid_id)
                success = await send_from_cache(event, vid_id, raw_cache, target)
                if success: return

            url = f"https://youtu.be/{vid_id}"
            wait_msg = await event.reply("⏳ جاري جلب البيانات والتحميل...")
            
            actual_file_path, info = await run_sync(download_audio_sync, url)
            
            if not actual_file_path or not os.path.exists(actual_file_path):
                raise Exception("فشل حفظ الملف الصوتي.")

            title = info.get('title', 'مقطع صوتي')
            duration = int(info.get('duration', 0))
            uploader = info.get('uploader', 'YouTube')
            duration_string = time.strftime('%M:%S', time.gmtime(duration))

            if duration > 3600:
                await wait_msg.delete()
                if os.path.exists(actual_file_path): os.remove(actual_file_path)
                return await event.reply("⚠️ المقطع طويل جداً (أكثر من ساعة).")

            uploaded_file = await fast_upload(ABH, actual_file_path)
            sent = await ABH.send_file(
                target,
                file=uploaded_file, 
                caption=f'@{channel} ~ {duration_string} ⏳',
                reply_to=event.id,
                attributes=[DocumentAttributeAudio(duration=duration, title=title, performer=uploader)]
            )
            
            await wait_msg.delete()            
            
            if sent and sent.media and hasattr(sent.media, 'document'):
                doc = sent.media.document
                r.set(f"ytvideo{vid_id}", json.dumps({
                    "audio_id": doc.id, 
                    "access_hash": doc.access_hash, 
                    "file_reference": doc.file_reference.hex(), 
                    "duration": duration,
                    "title": title,
                    "performer": uploader
                }))
                r.set(f"ytquery:{query_clean}", vid_id)
            
            if os.path.exists(actual_file_path): 
                os.remove(actual_file_path)
                
        except Exception as ex:
            err_msg = str(ex)
            if "Sign in" in err_msg or "cookie" in err_msg.lower():
                await event.reply("❌ حظر من يوتيوب: يرجى رفع ملف كوكيز (cookies.txt) جديد وصالح عبر البوت.")
            else:
                await event.reply(f"❌ حدث خطأ غير متوقع أثناء المعالجة: {err_msg}")

@ABH.on(events.NewMessage(pattern=r'^(/cookies|كوكيز)$'))
async def update_cookies_handler(event):
    # تحقق أولاً من أن المرسل هو المطور أو الأدمن (يمكنك تعديل الشرط حسب رغبتك)
    # مثال: if event.sender_id != DEVELOPER_ID: return
    
    # التحقق مما إذا كان الأمر رداً على ملف
    if not event.is_reply:
        return await event.reply("⚠️ يرجى إرسال ملف `cookies.txt` أولاً، ثم قم بالرد عليه بكتابة الأمر: `كوكيز` أو `/cookies`")
        
    reply_message = await event.get_reply_message()
    
    # التأكد من أن الرسالة التي يتم الرد عليها تحتوي على ملف (وثيقة)
    if not reply_message or not reply_message.file:
        return await event.reply("❌ الرسالة التي قمت بالرد عليها لا تحتوي على ملف!")
        
    # التحقق من أن امتداد الملف هو .txt
    if not reply_message.file.name or not reply_message.file.name.endswith('.txt'):
        return await event.reply("⚠️ خطأ في صيغة الملف! يجب أن يكون اسم الملف ينتهي بـ `.txt` (مثال: `cookies.txt`).")

    wait_msg = await event.reply("⏳ جاري فحص ملف الكوكيز وحفظه...")
    
    try:
        # مسار مؤقت لتحميل الملف والتأكد من بنيته
        temp_path = "temp_cookies.txt"
        await reply_message.download_media(file=temp_path)
        
        # قراءة محتوى الملف للتأكد من أنه كوكيز متوافق وليس نصاً عشوائياً
        with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # الكوكيز الصحيح الخاص بـ Netscape يجب أن يحتوي على ثوابت يوتيوب أو كلمة Netscape في البداية
        if "youtube.com" not in content and "# Netscape" not in content:
            if os.path.exists(temp_path): os.remove(temp_path)
            return await wait_msg.edit("❌ الملف المرفوع لا يبدو أنه يحتوي على كوكيز يوتيوب صالحة! تأكد من استخراجه بصيغة Netscape.")
            
        # إذا كان صالحاً، نقوم بنقله إلى المسار الرئيسي المستخدم في كود اليوتيوب
        # COOKIES_PATH تم تعريفه سابقاً بـ 'cookies.txt'
        if os.path.exists(COOKIES_PATH):
            os.remove(COOKIES_PATH)
            
        os.rename(temp_path, COOKIES_PATH)
        
        await wait_msg.edit("✅ تم تحديث ملف الكوكيز بنجاح! سيبدأ البوت الآن باستخدام الإعدادات الجديدة في عمليات التحميل القادمة.")
        
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        await wait_msg.edit(f"❌ حدث خطأ أثناء حفظ الملف: {str(e)}")
