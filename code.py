from telethon import events
import httpx
import asyncio
import io
from ABH import ABH as client

# الرابط والمعدات
URL = "https://us-central1-amor-ai.cloudfunctions.net/chatWithGPT"
HEADERS = {
    'User-Agent': "okhttp/5.0.0-alpha.2",
    'Content-Type': "application/json; charset=utf-8",
    'Accept': "application/json"
}

print("--- البوت شغال الآن (نسخة Telethon المستقرة) ---")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.raw_text:
        return

    async with client.action(event.chat_id, 'typing'):
        try:
            # تجهيز البيانات
            payload = {
                "data": {
                    "messages": [
                        {"role": "user", "content": event.raw_text}
                    ]
                }
            }
            
            async with httpx.AsyncClient() as http:
                # محاولة إرسال الطلب
                response = await http.post(URL, json=payload, headers=HEADERS, timeout=30.0)
                
                # فحص إذا كان الرد ناجحاً (200 OK)
                if response.status_code != 200:
                    await event.reply("⚠️ السيرفر مشغول حالياً، جرب لاحقاً.")
                    return

                data = response.json()

                # استخراج الرد مع الحماية من KeyError
                try:
                    result = data.get('result', {})
                    choices = result.get('choices', [])
                    if not choices:
                        await event.reply("❌ لم أتمكن من الحصول على رد من الذكاء الاصطناعي.")
                        return
                        
                    answer = choices[0].get('message', {}).get('content', '')
                except (AttributeError, IndexError):
                    await event.reply("⚙️ حدث تغيير في إعدادات السيرفر، يرجى تحديث الكود.")
                    return

            # التعامل مع الأكواد والنصوص
            if "```" in answer:
                # تقسيم النص للحصول على الكلام قبل الكود
                parts = answer.split("```")
                desc = parts[0].strip()
                code_content = parts[1].split("\n", 1)[-1] if "\n" in parts[1] else parts[1]
                
                if desc:
                    await event.reply(desc)
                
                # تحويل الكود لملف وإرساله
                file_data = io.BytesIO(code_content.strip().encode('utf-8'))
                file_data.name = "code.py"
                await client.send_file(event.chat_id, file_data, caption="✅ تم استخراج الكود")
            else:
                await event.reply(answer)

        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            await event.reply("⚠️ حدث خطأ تقني بسيط، أعد المحاولة.")

# التشغيل
client.run_until_disconnected()
