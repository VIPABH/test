import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

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
]

# قائمة الكلمات المحظورة بعد معالجتها
normalized_banned_words = {word: re.sub(r'(.)\1+', r'\1', word) for word in banned_words}

def normalize_text(text):
    """تحويل النص ليكون قابلًا للمقارنة بدون حذف الرموز"""
    text = text.lower()  # تحويل النص إلى حروف صغيرة
    replace_map = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}
    for old, new in replace_map.items():
        text = text.replace(old, new)
    text = re.sub(r'(.)\1+', r'\1', text)  # إزالة التكرار الزائد للحروف
    return text

def check_message(message):
    """التحقق مما إذا كانت الرسالة تحتوي على كلمة محظورة"""
    words = message.split()
    normalized_words = [normalize_text(word) for word in words]

    for word in normalized_words:
        if "ى" * 3 in word:  # إذا كانت الكلمة تحتوي على ىىى
            return True
        if word in normalized_banned_words.values():  # مقارنة بالكلمات المحظورة المعالجة مسبقًا
            return True

    return False

@ABH.on(events.NewMessage)
async def handler(event):
    """التعامل مع الرسائل"""
    if event.is_group:
        message_text = event.raw_text.strip()

        if message_text.startswith('#'):
            new_word = message_text[1:].strip()
            if new_word and new_word not in banned_words:
                banned_words.append(new_word)
                normalized_banned_words[new_word] = normalize_text(new_word)  # تحديث القائمة
                await event.reply(f"✅ تم إضافة الكلمة '{new_word}' إلى قائمة الكلمات المحظورة!")

        elif message_text.startswith('-'):
            remove_word = message_text[1:].strip()
            if remove_word in banned_words:
                banned_words.remove(remove_word)
                normalized_banned_words.pop(remove_word, None)  # إزالة من القائمة المعالجة
                await event.reply(f"❌ تم حذف الكلمة '{remove_word}' من قائمة الكلمات المحظورة!")

        elif check_message(event.raw_text):
            user_id = event.sender_id

            # تقييد المستخدم الذي أرسل الكلمة المحظورة
            chat = await event.get_chat()
            restrict_rights = ChatBannedRights(
                until_date=None,  # لا يوجد تاريخ انتهاء
                send_messages=True,  # منع إرسال الرسائل
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
            await ABH(EditBannedRequest(chat.id, user_id, restrict_rights))
            await event.delete()            
            await event.reply(f"⤶ المستخدم [{event.sender.first_name}](tg://user?id={event.sender_id}) \n تم تقييده لاستخدامه كلمة محظورة ☠")

# تشغيل البوت
print("✅ البوت شغال وينتظر الرسائل...")
ABH.run_until_disconnected()
