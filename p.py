import os
from telethon import TelegramClient, events

# جلب المتغيرات من البيئة
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# التحقق من أن جميع القيم موجودة
assert api_id and api_hash and bot_token, "يرجى التأكد من ضبط API_ID و API_HASH و BOT_TOKEN"

# تشغيل البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تخزين معلومات المستخدمين
uinfo = {}

# أوامر البوت
@ABH.on(events.NewMessage(pattern=r'^اوامري|اوامر$'))
async def start(event):
    await event.reply("""
**أوامر البوت المخفي** 卐

⌘ `اوامر التوب`  
   يحسب عدد رسائل مجموعتك.  

⌘ `اوامر التقييد`  
   أمر مكافح للكلمات غير اللائقة بنسبة 90%.  

⌘ `اوامر الالعاب`  
   ألعاب جديدة بفكرة مميزة ولمسة إبداعية.  

⌘ `اوامر الترجمة`  
   يعمل بالرد أو مع الأمر، لكن لا تستخدمه معهما معًا.  

⌘ `اوامر الايدي`  
   **أمر مميز** يمكنك من التواصل مع الشخص عبر معرف حسابه.  

⌘ `اوامر الكشف`  
   **أمر مميز** يأخذ لقطة شاشة للرابط، وتظهر الروابط الملغمة هنا.  

⌘ `اوامر الحسبان`  
   يحسب تواريخ أشهر الصيام والعزاء، أو أي يوم من اختيارك.  

⌘ `اوامر الميمز`  
   أوامر مخصصة لإنشاء الميمز بطرق مختلفة.  

⌘ `اوامر الهمسة`  
   أمر هزلي وسري لإنشاء همسة باستخدام اليوزر أو المعرف.  

⌘ `اوامر البحث`  
   يقوم بالبحث في موقع ويكيبيديا.  

⌘ `اوامر الصوتيات`  
   يرسل لك لطمية عشوائية. 
                       
⌘ `اوامر الذكاء`  
   ذكاء اصطناعي مبسط ليس اذكئ شيء.
""")

ABH.run_until_disconnected()
