from telethon import events
import httpx
import asyncio
import io
import re
from ABH import ABH as client

# API جديد (سريع ومباشر)
URL = "https://api.paxsenix.biz.id/ai/gpt4"

print("--- البوت شغال الآن ---")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.raw_text or event.out:
        return

    # إظهار حالة الكتابة للمستخدم
    async with client.action(event.chat_id, 'typing'):
        try:
            # محاولة جلب الرد
            async with httpx.AsyncClient(follow_redirects=True) as http:
                # استخدمنا params لتجنب مشاكل الرموز في الرابط
                response = await http.get(URL, params={'text': event.raw_text}, timeout=25.0)
                
                # طباعة الحالة في الكونسول للمطور (لك أنت)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    await event.reply("⚠️ السيرفر لا يستجيب، سأحاول مرة أخرى.")
                    return

                data = response.json()
                # جلب الرد من الحقل المتوقع
                await e.reply(str(data))
                answer = data.get('message', data.get('result', data.get('answer', '')))

            if not answer:
                await event.reply("⚠️ لم أتمكن من الحصول على رد مفيد.")
                return

            # التعامل مع الأكواد
            if "```" in answer:
                # استخراج النصوص والأكواد
                text_parts = re.split(r'```(?:\w+)?', answer)
                main_text = text_parts[0].strip()
                
                if main_text:
                    await event.reply(main_text)
                
                # استخراج أول كود تجده
                code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', answer, re.DOTALL)
                if code_match:
                    code_content = code_match.group(1)
                    file = io.BytesIO(code_content.strip().encode('utf-8'))
                    file.name = "code.py"
                    await client.send_file(event.chat_id, file, caption="✅ تم استخراج الكود بنجاح.")
            else:
                await event.reply(answer)

        except Exception as e:
            print(f"Error Detail: {e}") # هذا سيظهر لك في الشاشة السوداء
            await event.reply("⚠️ حدث خطأ تقني، يرجى المحاولة لاحقاً.")

# بدء التشغيل
client.run_until_disconnected()
