from telethon import events
import json
import urllib.request
import urllib.parse
from ABH import ABH as client
# ----------------------------
# إعداد المفاتيح
# ----------------------------
GEMINI_API_KEY = "AIzaSyCfoH1E0-8xexIUFHaZGnp-G58Cc2hegvM"
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# ----------------------------
# دالة إرسال الرسالة إلى Gemini
# ----------------------------
def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(GEMINI_URL, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return "⚠️ حدث خطأ أثناء الاتصال بخدمة Gemini API."

# ----------------------------
# الحدث الرئيسي (NewMessage)
# ----------------------------
@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    user_msg = event.raw_text.strip()
    chat_id = event.chat_id

        # تجاهل الأوامر لتجنب تداخل غير مقصود
    if user_msg.startswith("/start"):
        await event.respond("👋 أهلاً بك! أرسل أي رسالة وسأرد باستخدام Gemini.")
        return

    if not user_msg:
        return

        # استدعاء Gemini للرد
    reply = ask_gemini(user_msg)
    await event.respond(reply)