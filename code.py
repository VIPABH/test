import httpx
import json
from telethon import events
from ddgs import DDGS
from datetime import datetime

# --- الإعدادات (تأكد من وضع التوكن الخاص بك) ---
GROQ_API_KEY = "gsk_xxxx" 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# --- دالة البحث واستخراج الروابط ---
def search_web(query):
    search_data = []
    try:
        with DDGS() as ddgs:
            # جلب 3 نتائج مع الروابط والعناوين
            results = list(ddgs.text(query, max_results=3))
            if results:
                context = ""
                links = "\n\n**🔗 المصادر:**"
                for i, r in enumerate(results, 1):
                    context += f"[{i}] {r['body']}\n"
                    links += f"\n{i}. [{r['title']}]({r['href']})"
                return context, links
    except Exception as e:
        print(f"Search Error: {e}")
    return "", ""

# --- دالة الاتصال بالذكاء الاصطناعي ---
async def get_ai_reply(prompt_content):
    # إعداد الوقت واليوم باللغة العربية
    now = datetime.now().strftime("%A, %d %B %Y")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": (
                    f"أنت ذكاء اصطناعي متطور تدعى 'مخفي'، مطورك هو 'ابن هاشم'.\n"
                    f"تاريخ اليوم هو: {now}.\n\n"
                    "قواعد الإجابة:\n"
                    "1. سأزودك بمعلومات من الإنترنت حول سؤال المستخدم.\n"
                    "2. حلل المعلومات واستنتج الإجابة بدقة، ولا تكتفِ بنسخ النصوص.\n"
                    "3. قارن التواريخ في المعلومات مع تاريخ اليوم لتقديم أدق إجابة ممكنة.\n"
                    "4. لا تذكر جملة 'بناءً على المعلومات المتاحة'، أجب مباشرة كخبير.\n"
                    "5. إذا سألك أحد عن اسمك أجب بـ 'مخفي'، وعن مطورك أجب بـ 'ابن هاشم'."
                )
            },
            {"role": "user", "content": prompt_content}
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

# --- معالج الرسائل الرئيسي ---
@ABH.on(events.NewMessage(pattern=r"^مخفي(\s+.*|$)"))
async def bot_handler(event):
    user_q = event.pattern_match.group(1).strip()
    
    # دعم الرد (Reply)
    if not user_q and event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.text:
            user_q = reply_msg.text

    if not user_q:
        return

    async with event.client.action(event.chat_id, "typing"):
        # 1. تنفيذ البحث
        web_info, sources = search_web(user_q)
        
        # 2. تجهيز النص للذكاء الاصطناعي
        if web_info:
            full_prompt = f"معلومات الإنترنت:\n{web_info}\n\nسؤال المستخدم: {user_q}"
        else:
            full_prompt = user_q

        # 3. جلب الرد
        ai_res = await get_ai_reply(full_prompt)
        
        if ai_res:
            # دمج رد الذكاء الاصطناعي مع روابط المصادر
            final_response = f"{ai_res}{sources}"
            # استخدام دالة chs الخاصة بك للإرسال
            await chs(event, final_response)
