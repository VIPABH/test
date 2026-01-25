import asyncio, yt_dlp, os, re, uuid, json, logging
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r

# --- 1. تحديث دوال التعرف على الروابط ---
def get_media_info(url):
    """التعرف على نوع الرابط واستخراج المعرف"""
    yt_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    ig_pattern = r'instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)'
    
    yt_match = re.search(yt_pattern, url)
    if yt_match:
        return "youtube", yt_match.group(1)
        
    ig_match = re.search(ig_pattern, url)
    if ig_match:
        return "instagram", ig_match.group(1)
        
    return "other", str(uuid.uuid4())[:11]

# --- 2. معالج الرسائل المحدث ---
@ABH.on(events.NewMessage(incoming=True))
async def main_handler(e):
    if not e.is_private or not e.text: return
    text = e.text.strip()

    # دعم روابط يوتيوب وإنستغرام
    if "youtube.com" in text or "youtu.be" in text or "instagram.com" in text:
        platform, media_id = get_media_info(text)
        return await show_download_options(e, text, platform)
    
    # أوامر التحميل السريع من البحث
    elif text.startswith('/dl_'):
        vid = text.split('_')[1]
        return await show_download_options(e, f"https://youtu.be/{vid}", "youtube")
    
    # البحث العادي (يوتيوب فقط)
    elif not text.startswith('/'):
        try:
            results = await run_sync(lambda: Y88F8(text, max_results=5).to_dict())
            if not results: return await e.reply("❌ لم أجد نتائج.")
            msg = f"🔍 **نتائج البحث:**\n\n"
            for res in results:
                msg += f"• **{res['title']}**\n🔗 `/dl_{res['id']}`\n\n"
            await e.reply(msg, link_preview=False)
        except Exception as ex:
            await e.reply(f"❌ خطأ: {ex}")

# --- 3. عرض الخيارات مع تمييز المنصة ---
async def show_download_options(event, url, platform):
    _, media_id = get_media_info(url)
    short_id = str(uuid.uuid4())[:8]
    
    r.setex(f"yt_tmp:{short_id}", 600, json.dumps({
        "url": url, 
        "vid": media_id, 
        "u": event.sender_id,
        "p": platform
    }))
    
    # إنستغرام عادة يكون فيديو، لكن سنبقي خيار الصوت متاحاً
    buttons = [
        [Button.inline("🎥 تحميل فيديو", data=f"dl_v|{short_id}"),
         Button.inline("🎵 تحميل صوت", data=f"dl_a|{short_id}")]
    ]
    
    icon = "🎬" if platform == "youtube" else "📸"
    await event.reply(f"**{icon} منصة الميديا:** `{platform.upper()}`\n\nاختر الصيغة المطلوبة:", buttons=buttons)

# --- 4. معالج التحميل (دعم شامل) ---
@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    raw_data = e.data.decode('utf-8')
    type_dl, short_id = raw_data.split("|")
    
    raw_tmp = r.get(f"yt_tmp:{short_id}")
    if not raw_tmp: return await e.answer("⚠️ الطلب قديم.", alert=True)
    
    tmp_data = json.loads(raw_tmp)
    if tmp_data['u'] != e.sender_id:
        return await e.answer("⚠️ هذا الطلب لغيرك.", alert=True)

    url, platform = tmp_data['url'], tmp_data['p']
    await e.edit(f"⏳ جاري سحب ميديا من {platform}...")

    file_path = f"downloads/{uuid.uuid4().hex}"
    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "no_warnings": True,
        # إضافة ملف تعريف الارتباط (Cookies) إذا كان الحساب خاصاً أو هناك حظر
        # "cookiefile": "cookies.txt", 
    }

    if type_dl == "dl_v":
        # لإنستغرام، نفضل mp4 دائماً لسهولة التشغيل
        ydl_ops["format"] = "bestvideo+bestaudio/best" if platform == "youtube" else "best"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        info = await run_sync(execute_download, ydl_ops, url)
        actual_file = f"{file_path}.mp3" if type_dl == "dl_a" else (info.get('filepath') or f"{file_path}.mp4")
        
        # تصحيح الامتدادات المفاجئة من إنستغرام (مثل .webm)
        if not os.path.exists(actual_file):
            for ext in [".mp4", ".mkv", ".webm"]:
                if os.path.exists(f"{file_path}{ext}"):
                    actual_file = f"{file_path}{ext}"
                    break

        await ABH.send_file(
            e.chat_id, 
            actual_file, 
            caption=f"✅ **تم التحميل من {platform}**\n👤 @{ (await e.get_sender()).username or 'User' }",
            supports_streaming=True
        )
        await e.delete()
    except Exception as ex:
        await e.edit(f"❌ فشل تحميل المقطع.\nالسبب: قد يكون الحساب خاصاً أو الرابط غير صالح.")
    finally:
        # تنظيف شامل
        for f in os.listdir("downloads"):
            if f.startswith(os.path.basename(file_path)):
                os.remove(os.path.join("downloads", f))
