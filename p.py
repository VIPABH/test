from telethon import TelegramClient, events
from telethon.tl import EditBannedRequest
import os
import re

# جلب البيانات من متغيرات البيئة
api_id = int(os.getenv('API_ID'))      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN') 

# تشغيل البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# قائمة الكلمات المحظورة
banned_words = [
    "سب", "كس", "عير", "كسمك", "كسختك", "كس امك", "طيز", "طيزك", "فرخ", "كواد", 
    "انيجك", "نيجك", "كحبة", "ابن الكحبة", "ابن الكحبه", "تنيج", "اتنيج", "ينيج", 
    "اينيج", "بربوك", "زب", "طيزها", "عيري", "خرب الله", "العير", "بعيري", "كحبه", 
    "برابيك", "نيجني", "نيچني", "نودز", "نتلاوط", "لواط", "لوطي", "فروخ", "منيوك", 
    "مايا", "ماية", "مايه", "بكسمك", "بكسختك", "🍑", "نغل", "نغولة", "نغوله", "ينغل", 
    "سكسي", "كحاب", "مناويج", "منيوج", "عيورة", "عيورتكم", "انيجة", "انيچة", "انيجه", 
    "انيچه", "أناج", "اناج", "انيج", "أنيج", "فريخ", "فريخة", "فريخه", "فرخي", "🍆", 
    "🖕", "كسك", "كسه", "كسة", "اكحاب", "أكحاب", "زنا", "كوم بي", "كمبي", "ارقة جاي", 
    "ارقه جاي", "يموط", "تموط", "موطلي", "اموط", "بورن", "الفرخ", "الفرحْ", "تيز", "كسم"
]  # إضافة الكلمات المحظورة

def normalize_text(text):
    """إزالة كل شيء عدا الأحرف مع إزالة الأرقام والحروف 'ـ' و 'ى'"""
    # إزالة أي شيء غير حرف أو الأرقام
    text = re.sub(r'[^أ-يa-zA-Z]', '', text)  # إزالة كل شيء عدا الحروف والأحرف
    # إزالة مجموعة من الأحرف بما فيها 'ڤ'
    remove_chars = ['پ', 'ڤ', 'هـ', 'چ', 'گ', 'أ', 'إ', 'آ', 'ئ', 'ژ']
    for char in remove_chars:
        text = text.replace(char, '')  # إزالة الحروف المحددة
    text = text.replace('ـ', '')  # إزالة الحرف 'ـ'
    text = text.replace('ى', '')  # إزالة الحرف 'ى'
    text = re.sub(r'(.)\1+', r'\1', text)  # إزالة الحروف المكررة
    return text

def check_message(message):
    """التحقق مما إذا كانت الرسالة تحتوي على كلمة محظورة حتى لو كان فيها حروف مكررة"""
    words = message.split()  # تقسيم الرسالة إلى كلمات منفصلة
    normalized_words = [normalize_text(word) for word in words]  # تنظيف كل كلمة
    
    # التحقق من وجود "ىىى" في أي كلمة
    for word in normalized_words:
        if "ى" * 3 in word:  # إذا كانت الكلمة تحتوي على ىىى
            return True
    
    for banned_word in banned_words:
        if normalize_text(banned_word) in normalized_words:  # تطابق 100% بعد المعالجة
            return True
    return False

@ABH.on(events.NewMessage)
async def handler(event):
    """التعامل مع الرسائل"""
    # التحقق من أن الرسالة تأتي من مجموعة
    if event.is_group:  # إذا كانت الرسالة في مجموعة
        # إضافة كلمات محظورة جديدة باستخدام علامة #
        if event.raw_text.startswith('#'):
            new_word = event.raw_text[1:].strip()  # إزالة العلامة #
            if new_word not in banned_words:  # إذا لم تكن الكلمة موجودة من قبل
                banned_words.append(new_word)  # إضافتها إلى القائمة
                await event.reply(f"✅ تم إضافة الكلمة '{new_word}' إلى قائمة الكلمات المحظورة!")
        
        elif check_message(event.raw_text):
            user_id = event.sender_id
            warning_msg = "🚨 **تحذير:** لا يمكنك استخدام كلمات محظورة في المحادثة! 🚫"
            await event.reply(warning_msg)  # إرسال رسالة تحذير

            # تقييد المرسل
            try:
                # تقييد المرسل من إرسال الرسائل في المجموعة لمدة غير محددة
                await event.client(EditBannedRequest(event.chat_id, user_id, send_messages=False))
                await event.reply("🚫 تم تقييدك من إرسال الرسائل في هذه المجموعة بسبب استخدام كلمات محظورة!")
            except Exception as e:
                print(f"Error while restricting user: {e}")

# تشغيل البوت
print("✅ البوت شغال وينتظر الرسائل...")
ABH.run_until_disconnected()
