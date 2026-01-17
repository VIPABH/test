from telethon import events
import httpx
import asyncio
import io
from ABH import ABH as client

# إعدادات الرابط
URL = "https://us-central1-amor-ai.cloudfunctions.net/chatWithGPT"
HEADERS = {
    'User-Agent': "okhttp/5.0.0-alpha.2",
    'Content-Type': "application/json; charset=utf-8"
}

print("--- البوت شغال الآن (تليثون) ---")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # تجاهل الرسائل إذا لم يكن لها نص
    if not event.raw_text:
        return

    user_text = event.raw_text
    
    async with client.action(event.chat_id, 'typing'):
        try:
            payload = {"data": {"messages": [{"role": "user", "content": user_text}]}}
            
            async with httpx.AsyncClient() as http:
                response = await http.post(URL, json=payload, headers=HEADERS, timeout=30.0)
                data = response.json()

                # فحص وجود 'result' لتجنب KeyError
                if 'result' in data and 'choices' in data['result']:
                    answer = data['result']['choices'][0]['message']['content']
                else:
                    await event.reply("⚠️ اعتذر، لم أتمكن من معالجة طلبك حالياً.")
                    return

            # معالجة النصوص والأكواد
            if "```" in answer:
                parts = answer.split("```")
                text_part = parts[0].strip()
                code_part = parts[1].split("\n", 1)[-1] if "\n" in parts[1] else parts[1] # تنظيف لغة البرمجة إن وجدت
                
                if text_part:
                    await event.reply(text_part)
                
                file = io.BytesIO(code_part.strip().encode())
                file.name = "code.py"
                await client.send_file(event.chat_id, file, caption="✅ تم استخراج الكود بنجاح")
            else:
                await event.reply(answer)

        except Exception as e:
            # طباعة الخطأ في الكونسول للتصحيح وإرسال رسالة بسيطة للمستخدم
            print(f"Error: {e}")
            await event.reply("حدث خطأ في الاتصال بالسيرفر، حاول مجدداً لاحقاً.")

# لا حاجة لـ client.run_until_disconnected() إذا كان ملف ABH يتعامل مع هذا بالفعل
client.run_until_disconnected()
