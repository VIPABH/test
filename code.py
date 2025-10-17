from telethon import events
import aiohttp
import asyncio
import json
from ABH import ABH as client

# ----------------------------
# إعداد المفاتيح والموديل
# ----------------------------
GEMINI_API_KEY = "AIzaSyCfoH1E0-8xexIUFHaZGnp-G58Cc2hegvM"
GEMINI_MODEL = "gemini-2.5-flash-lite"  # ⚡ أسرع إصدار من Gemini
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ----------------------------
# دالة غير متزامنة للتحدث مع Gemini
# ----------------------------
async def ask_gemini(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    body = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GEMINI_URL, headers=headers, json=body, timeout=25) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    err = await resp.text()
                    print(f"❌ HTTP Error {resp.status}: {err}")
                    return f"⚠️ خطأ في الاتصال بخدمة Gemini API (رمز: {resp.status})"
    except asyncio.TimeoutError:
        return "⏱️ انتهت مهلة الاتصال، حاول مجددًا."
    except Exception as e:
        return f"⚠️ خطأ غير متوقع: {str(e)}"

# ----------------------------
# الحدث الرئيسي (غير متزامن بالكامل)
# ----------------------------
@client.on(events.NewMessage(pattern=r"^مخفي\s+"))
async def handle_hidden_message(event):
    user_msg = event.raw_text.strip()
    
    # إزالة كلمة "مخفي " من بداية الرسالة
    prompt = user_msg[len("مخفي "):]

    if not prompt:
        await event.respond("⚠️ الرجاء كتابة نص بعد كلمة 'مخفي'.")
        return

    # إرسال رسالة انتظار مؤقتة
    

    # استدعاء Gemini
    reply = await ask_gemini(prompt)

    # تحديث الرد النهائي
    await event.reply(reply)