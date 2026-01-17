from telethon import TelegramClient, events
import httpx
import asyncio
import io
from ABH import ABH as client
# إعدادات البوت - ضع معلوماتك هنا
URL = "https://us-central1-amor-ai.cloudfunctions.net/chatWithGPT"

# إنشاء العميل

print("--- البوت شغال الآن ---")

@client.on(events.NewMessage)
async def handler(event):
    # تجاهل الرسائل الصادرة من البوت نفسه
    if event.out:
        return

    user_text = event.raw_text
    
    # إظهار حالة "جاري الكتابة"
    async with client.action(event.chat_id, 'typing'):
        try:
            # إرسال الطلب للموقع
            payload = {"data": {"messages": [{"role": "user", "content": user_text}]}}
            async with httpx.AsyncClient() as http:
                response = await http.post(URL, json=payload, timeout=20.0)
                data = response.json()
                answer = data['result']['choices'][0]['message']['content']

            # إذا كان الرد يحتوي على كود برمجي، نستخرجه ونرسله كملف
            if "```" in answer:
                # إرسال النص أولاً
                clean_text = answer.split("```")[0]
                if clean_text:
                    await event.reply(clean_text)
                
                # استخراج الكود (بشكل بسيط)
                code = answer.split("```")[1].split("```")[0]
                file = io.BytesIO(code.strip().encode())
                file.name = "code.py"
                await client.send_file(event.chat_id, file, caption="تفضل، هذا هو الكود المطلوب")
            else:
                # رد نصي عادي
                await event.reply(answer)

        except Exception as e:
            await event.reply(f"حدث خطأ بسيط: {str(e)}")

client.run_until_disconnected()
