from telethon import events
import json
import urllib.request
from ABH import ABH as client

# ----------------------------
# إعداد المفاتيح والموديل
# ----------------------------
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"  # ✅ النموذج المستقر حسب آخر تحديث
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ----------------------------
# دالة التواصل مع Gemini
# ----------------------------
def ask_gemini(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    body = json.dumps({
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }).encode()

    req = urllib.request.Request(GEMINI_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        print("❌ HTTP Error:", e.code, e.read().decode())
        return f"⚠️ خطأ في الاتصال بخدمة Gemini API (رمز: {e.code})"
    except Exception as e:
        print("❌ Exception:", str(e))
        return "⚠️ حدث خطأ غير متوقع أثناء الاتصال بـ Gemini."

# ----------------------------
# الحدث الرئيسي في البوت
# ----------------------------
@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    user_msg = event.raw_text.strip()

    if user_msg.startswith("/start"):
        await event.respond("👋 مرحبًا! أرسل لي أي نص وسأرد باستخدام Google Gemini 2.5 Flash.")
        return

    if not user_msg:
        return

    reply = ask_gemini(user_msg)
    await event.respond(reply)