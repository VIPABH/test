import httpx
import asyncio
import time

async def test_my_ai():
    # 1. تحديد الرابط مباشرة للتأكد من نجاح التجربة
    url = "http://93.127.134.217:11434/api/chat"
    model_name = "llama3.1"
    
    print(f"--- 🛠️ بدء عملية الفحص ---")
    print(f"📍 الرابط المستهدف: {url}")
    print(f"🤖 النموذج المطلوب: {model_name}")

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومختصر جداً."},
            {"role": "user", "content": "مرحبا، من أنت؟"}
        ],
        "stream": False
    }

    print("⏳ الخطوة 1: محاولة فتح اتصال مع السيرفر...")
    
    start_time = time.time()
    
    try:
        # استخدام timeout طويل لأن الـ CPU يحتاج وقت لتحميل الموديل
        async with httpx.AsyncClient(timeout=120.0) as client:
            
            print("📤 الخطوة 2: إرسال البيانات (Payload) وانتظار المعالجة...")
            response = await client.post(url, json=payload)
            
            print(f"📥 الخطوة 3: استلام رد من السيرفر (كود الحالة: {response.status_code})")
            
            if response.status_code == 200:
                print("✨ الخطوة 4: تحليل البيانات المستلمة (Parsing JSON)...")
                result = response.json()
                end_time = time.time()
                
                print("\n" + "="*30)
                print("✅ النتيجة النهائية:")
                print(f"🤖 الرد: {result['message']['content']}")
                print(f"⏱️ زمن الاستجابة الكامل: {round(end_time - start_time, 2)} ثانية")
                print("="*30)
            else:
                print(f"❌ فشل في الطلب. نص الخطأ من السيرفر: {response.text}")
                
    except httpx.ConnectError:
        print("⚠️ خطأ: تعذر الاتصال بالسيرفر. تأكد أن Ollama يعمل وأن البورت 11434 مفتوح.")
    except httpx.TimeoutException:
        print("⚠️ خطأ: انتهى الوقت (Timeout). السيرفر استغرق أكثر من دقيقتين للرد.")
    except Exception as e:
        print(f"⚠️ حدث خطأ غير متوقع: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(test_my_ai())
