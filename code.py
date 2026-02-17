import httpx
import asyncio
import time, os

async def test_my_ai():
    # رابط سيرفرك اللي جهزناه
    url = os.getenv("ip")
    
    # السؤال اللي بنجرب فيه
    payload = {
        "model": "llama3.1",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومختصر جداً."},
            {"role": "user", "content": "مرحبا، هل تسمعني؟ من أنت؟"}
        ],
        "stream": False
    }

    print("🚀 جاري إرسال السؤال للسيرفر المحلي... (انتظر قليلاً)")
    
    start_time = time.time() # نبدأ حساب الوقت
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                end_time = time.time() # انتهى التفكير
                
                print("\n✅ تم الرد بنجاح!")
                print(f"🤖 الرد: {result['message']['content']}")
                print(f"⏱️ الوقت المستغرق: {round(end_time - start_time, 2)} ثانية")
            else:
                print(f"❌ فشل السيرفر: كود الخطأ {response.status_code}")
                
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء الاتصال: {e}")

# تشغيل التجربة
if __name__ == "__main__":
    asyncio.run(test_my_ai())
