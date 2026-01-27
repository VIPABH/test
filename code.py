import asyncio, yt_dlp, os, re, uuid, json, shutil
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from telethon import events, Button
from ABH import ABH, r 

# --- 1. استخراج الروابط (تيك توك وانستا حصراً) ---
def extract_media_data(text):
    # نمط إنستقرام (بوست، ريلز، فيديو)
    ig = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+))', text)
    # نمط تيك توك (بما في ذلك الروابط المختصرة vm و vt)
    tt = re.search(r'(https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[^\s]+)', text)

    if ig: return "instagram", ig.group(1)
    if tt: return "tiktok", tt.group(1)
    return None, None

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# --- 2. معالج الرسائل ---
@ABH.on(events.NewMessage(incoming=True))
async def handler(e):
    if not e.is_private or not e.text: return
    
    platform, url = extract_media_data(e.text.strip())
    
    if platform:
        sid = str(uuid.uuid4())[:8]
        # تخزين الرابط في رديس لمدة 10 دقائق
        r.setex(f"dl:{sid}", 600, json.dumps({"u": url, "p": platform, "id": e.sender_id}))
        
        btns = [
            [Button.inline(f"🎥 تحميل فيديو ({platform.upper()})", data=f"v|{sid}")],
            [Button.inline("🎵 تحميل صوت فقط", data=f"a|{sid}")]
        ]
        await e.reply(f"**📥 تم كشف رابط من {platform.capitalize()}**\nاختر الصيغة المطلوبة:", buttons=btns)

# --- 3. محرك التحميل المتطور ---
@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def dl_callback(e):
    raw = r.get(f"dl:{e.data.decode().split('|')[1]}")
    if not raw: return await e.answer("⚠️ الطلب قديم أو منتهي.")
    
    data = json.loads(raw)
    if data['id'] != e.sender_id: return await e.answer("⚠️ هذا الطلب ليس لك.")
    
    type_dl = e.data.decode().split('|')[0]
    asyncio.create_task(process_media(e, data, type_dl))

async def process_media(event, data, type_dl):
    uid = uuid.uuid4().hex
    task_dir = f"downloads/{uid}"
    os.makedirs(task_dir, exist_ok=True)
    file_path = f"{task_dir}/media"

    await event.edit(f"⏳ جاري سحب الميديا من **{data['p']}**...")

    # إعدادات متقدمة لتجاوز حماية التيك توك وانستا
    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
        }
    }

    if type_dl == 'v':
        # تيك توك يحتاج أحياناً 'best' فقط بدون تفصيل لضمان عدم حدوث خطأ 10231
        ydl_ops["format"] = "bestvideo+bestaudio/best" if data['p'] == 'instagram' else "best"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = await run_sync(ydl.extract_info, data['u'], True)
            
        file_name = next((f"{task_dir}/{f}" for f in os.listdir(task_dir) if f.startswith("media")), None)
        if not file_name: raise Exception("فشل في العثور على الملف")

        if type_dl == 'v':
            await ABH.send_file(
                event.chat_id, file_name,
                caption=f"✅ **تم التحميل من {data['p']}**\n👤 `{info.get('uploader', 'Unknown')}`",
                attributes=[DocumentAttributeVideo(
                    duration=int(info.get('duration', 0)),
                    w=info.get('width', 0), h=info.get('height', 0),
                    supports_streaming=True
                )]
            )
        else:
            await ABH.send_file(
                event.chat_id, file_name,
                caption=f"🎵 **صوت من {data['p']}**",
                attributes=[DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'))]
            )
        
        await event.delete()

    except Exception as ex:
        await event.edit(f"❌ **فشل التحميل:**\nالمشكلة: `{str(ex)[:100]}`\n\n*ملاحظة: تأكد من أن الحساب ليس خاصاً (Private).*")
    
    finally:
        await run_sync(lambda: shutil.rmtree(task_dir, ignore_errors=True))

print("🚀 بوت التحميل (تيك توك + انستا) جاهز للعمل!")
