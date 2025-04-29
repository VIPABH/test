import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_dlp
from google.auth.transport.requests import Request
from telethon import TelegramClient, events

# إعدادات Telegram
api_id = os.getenv('API_ID')  # الحصول على API_ID من البيئة
api_hash = os.getenv('API_HASH')  # الحصول على API_HASH من البيئة
bot_token = os.getenv('BOT_TOKEN')  # الحصول على توكن البوت من البيئة

client = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)  # إعداد البوت باستخدام Telethon

# إعدادات Google API
CLIENT_SECRETS_FILE = "cookies.txt"  # مسار ملف Client Secret الذي حصلت عليه من Google Developer Console
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']  # نطاق الوصول للمحتوى

# دالة للمصادقة والحصول على بيانات المستخدم
def get_authenticated_service():
    credentials = None
    # إذا كان لدى المستخدم بيانات اعتماد محفوظة مسبقًا
    if os.path.exists('token.json'):
        credentials = google.auth.credentials.Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # إذا كانت بيانات الاعتماد غير موجودة أو منتهية الصلاحية
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            # منع فتح المتصفح واستخدام رابط بدلاً من ذلك
            flow.run_local_server(port=0, authorization_prompt_message="Please visit this URL: {url}")
            credentials = flow.credentials
        
        # حفظ بيانات الاعتماد للاستخدام المستقبلي
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    
    return googleapiclient.discovery.build(API_NAME, API_VERSION, credentials=credentials)

# دالة لتحميل الفيديو باستخدام yt-dlp
def download_video(video_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # لتحميل أفضل فيديو وصوت
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # تحديد اسم مجلد التحميل
        'noplaylist': True,  # لتجنب تحميل قوائم التشغيل
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_file = ydl.prepare_filename(info)
        return video_file  # إرجاع اسم الملف الذي تم تحميله

# دالة للبحث عن الفيديو على YouTube باستخدام API
def search_video(query):
    youtube = get_authenticated_service()  # الحصول على خدمة YouTube المعتمدة
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video"
    )
    response = request.execute()

    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    else:
        return None

# تحميل الفيديو عبر YouTube API
def download_from_youtube(query):
    video_url = search_video(query)
    if video_url:
        print(f"تم العثور على الفيديو: {video_url}")
        video_file = download_video(video_url)
        print(f"تم تحميل الفيديو: {video_file}")
        return video_file
    else:
        print("لم يتم العثور على الفيديو.")
        return None

# التعامل مع الرسائل الواردة في Telegram
@client.on(events.NewMessage(pattern='/فيديو'))
async def video_handler(event):
    try:
        video_query = event.text.split(None, 1)[1]  # استخراج استعلام الفيديو من الرسالة
    except IndexError:
        await event.reply("يرجى إرسال استعلام الفيديو مع الأمر.")
        return

    try:
        # تحميل الفيديو
        video_file = download_from_youtube(video_query)
        if video_file:
            await event.reply(file=video_file)  # إرسال الفيديو إلى المستخدم
            os.remove(video_file)  # حذف الملف بعد إرساله لتوفير المساحة
        else:
            await event.reply("لم يتم العثور على الفيديو.")
    except Exception as e:
        await event.reply(f'حدث خطأ أثناء تحميل الفيديو: {str(e)}')

# تشغيل البوت
if __name__ == "__main__":
    client.run_until_disconnected()  # يشغل البوت إلى أن يتم قطع الاتصال
