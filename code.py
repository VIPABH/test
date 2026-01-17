from telethon import events
import httpx
import asyncio
import io
import re
from ABH import ABH as client

# رابط API جديد ومستقر (يقدم استجابة سريعة)
URL = "https://api.paxsenix.biz.id/ai/gpt4"

print("--- البوت شغال الآن (بواسطة API جديد) ---")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # تجاهل الرسائل الفارغة أو الصادرة من البوت
    if not event.raw_text or event.out:
        return

    user_text = event.raw_text
    
    # إظهار حالة الكتابة
    async with client.action(event.chat_id, 'typing'):
        try:
            # طلب بسيط جداً للـ API الجديد
            async with httpx.AsyncClient() as http:
                response = await http.get(f"{URL}?text={user_text}", timeout=30.0)
                
                if response.status_code != 200:
                    await event.reply("⚠️ عذراً، السيرفر لا يستجيب حالياً.")
                    return

                data = response.json()
                # استخراج الرد (API Paxsenix عادة يرجع النتيجة في حقل 'message' أو 'result')
                answer = data.get('message', data.get('result', 'لم أجد رداً.'))

            # التعامل مع الأكواد (إذا وجد كود يرسله كملف)
            if "```" in answer:
                # استخراج النص قبل الكود
                text_before = answer.split("```")[0].strip()
                if text_before:
                    await event.reply(text_before)
                
                # استخراج محتوى الكود
                code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', answer, re.DOTALL)
                if code_match:
                    code_content = code_match.group(1)
                else:
                    code_content = answer.split("```")[1]

                file = io.BytesIO(code_content.strip().encode('utf-8'))
                file.name = "code.py"
                await client.send_file(event.chat_id, file, caption="✅ تم استخراج الكود بنجاح")
            else:
                await event.reply(answer)

        except Exception as e:
            print(f"Error: {e}")
            await event.reply("❌ حدث خطأ في الاتصال، حاول مرة أخرى.")

# تشغيل البوت
client.run_until_disconnected()
