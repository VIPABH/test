import json
import httpx
from telethon import events, Button
from ABH import ABH as bot

# دالة إرسال الطلب للسيرفر (تم تحويلها لـ async لتناسب تليثون)
async def ask_gpt(msg):
    u = "https://us-central1-amor-ai.cloudfunctions.net/chatWithGPT"
    p = {"data": {"messages": [{"role": "user", "content": msg}]}}
    h = {
        'User-Agent': "okhttp/5.0.0-alpha.2",
        'content-type': "application/json; charset=utf-8"
    }
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(u, json=p, headers=h, timeout=30.0)
            data = r.json()
            return data['result']['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ خطأ في الاتصال بالسيرفر: {str(e)}"

# معالج أمر /start مع زر إنلاين
@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    buttons = [Button.inline('بدء المحادثة مع GPT', b'start_chat')]
    await event.respond(
        "أهلاً بك! اضغط على الزر لبدء المحادثة مع الذكاء الاصطناعي.",
        buttons=buttons
    )

# معالج الضغط على الزر
@bot.on(events.CallbackQuery(data=b'start_chat'))
async def start_chat(event):
    await event.respond("تم بدء المحادثة. اكتب أي شيء للبدء (أرسل 'انهاء' للإغلاق).")
    # في تليثون، المحادثة تتم عبر الأحداث مباشرة بدون تسجيل خطوة تالية معقد
    # سنعتمد على استقبال الرسائل العادية

# معالج المحادثة المستمرة
@bot.on(events.NewMessage(incoming=True))
async def handle_conversation(event):
    # تجاهل الأوامر مثل /start
    if event.text.startswith('/'):
        return
        
    if event.text == 'انهاء':
        await event.respond("تم إنهاء المحادثة. اكتب /start للبدء من جديد.")
        return

    # إظهار حالة "جاري الكتابة"
    async with bot.action(event.chat_id, 'typing'):
        response = await ask_gpt(event.text)
        await event.reply(response)

print("--- البوت يعمل الآن (Telethon) ---")
bot.run_until_disconnected()
