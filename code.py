from ABH import *
import asyncio, yt_dlp, json, os, time, urllib.request
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from concurrent.futures import ThreadPoolExecutor
from Resources import *
YDL_TIKTOK_OPTS = {
    "format": "bestvideo+bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    # "cookiefile": COOKIES_PATH,
    "outtmpl": "downloads/tt_%(id)s.%(ext)s",
    "add_header": [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ],
}

@ABH.on(events.NewMessage(pattern='^(توك|تيك|تيكتوك|tt) ?(.*)'))
async def tiktok_func(e):
    target = e.chat_id        
    query = e.pattern_match.group(2)    
    if not query:
        re_msg = await e.get_reply_message()
        if re_msg and re_msg.text: 
            query = re_msg.text
        else: 
            return await e.reply("ارسل رابط فيديو التيك توك مع الأمر")

    if "tiktok.com" not in query:
        return await e.reply("⚠️ يرجى إرسال رابط تيك توك صحيح.")

    clean_url = query.strip().split("?")[0]
    track_id = clean_url.split("/video/")[-1].replace("/", "_") if "/video/" in clean_url else clean_url.split("tiktok.com/")[-1].replace("/", "_")
    cache_key = f"ttvideo_{track_id}"

    cache_data = get_from_cache_system(cache_key)
    if cache_data:
        try:
            file_input = InputDocument(
                id=cache_data["video_id"], 
                access_hash=cache_data["access_hash"], 
                file_reference=bytes.fromhex(cache_data["file_reference"])
            )
            await ABH.send_file(
                target, file_input, 
                reply_to=e.id,
                caption=cache_data.get("caption", "")
            )
            return
        except:
            delete_from_cache_system(cache_key)

    wait_msg = None
    actual_path = None
    reply_to_use = e.id
    
    async with download_semaphore:
        try:
            if l:
                wait_msg = await e.reply("⏳ جاري معالجة وتحميل فيديو التيك توك...")

            fast_opts = {"quiet": True, "cookiefile": COOKIES_PATH, "nocheckcertificate": True}
            with yt_dlp.YoutubeDL(fast_opts) as ydl:
                info = await run_sync(ydl.extract_info, query, False)
            
            if not info:
                return await e.reply("❌ تعذر جلب معلومات الفيديو، قد يكون خاصاً أو محذوفاً.")

            video_id = info.get('id', str(int(time.time())))
            title = info.get('title', 'TikTok Video')
            uploader = info.get('uploader', 'TikTok')
            caption_text = f"👤 **المصمم:** {uploader}\n📝 **الوصف:** {title}"

            opts = YDL_TIKTOK_OPTS.copy()
            opts["outtmpl"] = f"downloads/tt_{video_id}.%(ext)s"
            
            await run_sync(lambda: yt_dlp.YoutubeDL(opts).download([query]))
            
            actual_path = f"downloads/tt_{video_id}.mp4"
            if not os.path.exists(actual_path):
                for ext in ['mkv', 'webm', 'mov']:
                    test_path = f"downloads/tt_{video_id}.{ext}"
                    if os.path.exists(test_path):
                        actual_path = test_path
                        break

            if not os.path.exists(actual_path):
                raise Exception("فشل العثور على ملف الفيديو المنزّل في السيرفر.")

            uploaded_file = await fast_upload(ABH, actual_path)
            
            try:
                sent = await ABH.send_file(
                    target,
                    file=uploaded_file, 
                    caption=caption_text,
                    reply_to=e.id,
                    supports_streaming=True
                )
                if wait_msg:
                    try: await ABH.edit_message(target, message=wait_msg.id, text=f"[Enjoy Video](https://t.me/{BOT_FIRST_NAME})", link_preview=False)
                    except: pass
            except Exception as send_err:
                reply_to_use = e.id if "REPLY_MESSAGE_ID_INVALID" not in str(send_err) else None
                sent = await ABH.send_file(
                    target,
                    file=uploaded_file, 
                    caption=caption_text,
                    reply_to=reply_to_use,
                    supports_streaming=True
                )
                if wait_msg:
                    try: await wait_msg.delete()
                    except: pass

            if sent and hasattr(sent, 'media') and sent.media and hasattr(sent.media, 'document') and sent.media.document:
                doc = sent.media.document
                r.incr("tiktok_videos_count")
                set_to_cache_system(cache_key, {
                    "video_id": doc.id, 
                    "access_hash": doc.access_hash, 
                    "file_reference": doc.file_reference.hex(),
                    "caption": caption_text
                })

        except Exception as ex:
            await e.reply(f"❌ حدث خطأ أثناء تحميل التيك توك: {str(ex)}")
        finally:
            if wait_msg and not reply_to_use:
                try: await wait_msg.delete()
                except: pass
            if actual_path and os.path.exists(actual_path):
                try: os.remove(actual_path)
                except: pass
