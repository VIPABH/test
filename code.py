from ABH import *
import httpx
import os
from telethon import events, Button # استيراد Button للتعامل مع الأزرار
from ddgs import DDGS
from datetime import datetime

GROQ_API_KEY = os.getenv('key') 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# دالة البحث المتقدم
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5)) # زيادة النتائج للبحث المتقدم
            if results:
                context = ""
                links = "\n\n**🌐 المصادر والنتائج المتقدمة:**"
                for i, r in enumerate(results, 1):
                    context += f"[{i}] {r['body']}\n"
                    links += f"\n{i}. [{r['title']}]({r['href']})"
                return context, links
    except Exception as e:
        print(f"Search Error: {e}")
    return "", ""

# دالة الذكاء الاصطناعي (مبسطة للرد السريع)
async def get_ai_reply(prompt_content, web_info=None):
    now = datetime.now().strftime("%A, %d %B %Y")
    system_msg = f"أنت 'مخفي'، مطورك 'ابن هاشم'. تاريخ اليوم: {now}."
    
    if web_info:
        system_msg += "\nاستخدم معلومات البحث المرفقة لتقديم إجابة تفصيلية ومحدثة."
        content = f"معلومات البحث:\n{web_info}\n\nسؤال المستخدم: {prompt_content}"
    else:
        content = prompt_content

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": content}
        ],
        "temperature": 0.6
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(GROQ_URL, json=payload, headers=headers)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
    except:
        return None

# معالج أمر "مخفي" (الرد السريع فقط)
@ABH.on(events.NewMessage(pattern=r"^مخفي(\s+.*|$)"))
async def bot_handler(event):
    user_q = event.pattern_match.group(1).strip()
    if not user_q and event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.text:
            user_q = reply_msg.text
    if not user_q: return

    async with event.client.action(event.chat_id, "typing"):
        # طلب الذكاء الاصطناعي بدون انتظار البحث
        ai_res = await get_ai_reply(user_q)
        
        if ai_res:
            # إضافة زر الإنلاين
            # نضع نص السؤال في الـ data لكي نعرف عما يبحث المستخدم عند الضغط
            buttons = [Button.inline("🔍 بحث متقدم ومصادر", data=f"search_{event.id}")]
            await event.reply(ai_res, buttons=buttons)

# معالج الضغط على الأزرار (البحث المتقدم)
@ABH.on(events.CallbackQuery(pattern=r"search_(\d+)"))
async def search_callback(event):
    # جلب الرسالة الأصلية التي تحتوي على السؤال
    msg = await event.get_message()
    reply_to = await msg.get_reply_message()
    
    # استخراج نص السؤال الأصلي
    if reply_to and reply_to.text:
        query = reply_to.text.replace("مخفي", "").strip()
    else:
        # إذا لم يجد السؤال الأصلي، نحاول استنتاجه أو تجاهله
        await event.answer("تعذر العثور على السؤال الأصلي.", alert=True)
        return

    await event.answer("جاري إجراء بحث متقدم... 🔎")
    
    # تنفيذ البحث والذكاء المتقدم
    web_info, sources = search_web(query)
    if web_info:
        advanced_res = await get_ai_reply(query, web_info=web_info)
        final_text = f"**📌 نتيجة البحث المتقدم:**\n\n{advanced_res}{sources}"
        # تعديل الرسالة الأصلية لإضافة النتائج
        await event.edit(final_text, buttons=None)
    else:
        await event.answer("لم أجد نتائج إضافية في الويب.", alert=True)
