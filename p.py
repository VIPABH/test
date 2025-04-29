import os
import google_auth_oauthlib.flow
import google.auth.transport.requests
from googleapiclient.discovery import build

# تحديد معلومات OAuth
CLIENT_SECRETS_FILE = "YOUR_CLIENT_SECRET_FILE.json"
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']  # النطاقات التي تريد الوصول إليها

# إعداد OAuth
def authenticate_youtube_oauth():
    # تحميل البيانات
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)

    # عملية المصادقة
    credentials = flow.run_local_server(port=8080)
    
    # بناء الخدمة
    youtube = build(API_NAME, API_VERSION, credentials=credentials)
    return youtube
