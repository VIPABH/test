import os
from telethon import TelegramClient, events
import asyncio
import re
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator
import asyncio
import re
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator
# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

banned_words = [
    "خرب دينه", "كسك", "كسه", "كسة", "اكحاب", "أكحاب", "زنا", "كوم بي", "كمبي", "ارقة جاي", 
    "ارقه جاي", "يموط", "تموط", "موطلي", "اموط", "بورن", "الفرخ", "الفرحْ", "تيز", "كسم",
    "سكسي", "كحاب", "مناويج", "منيوج", "عيورة", "عيورتكم", "انيجة", "انيچة", "انيجه", 
    "مايا", "ماية", "مايه", "بكسمك", "بكسختك", "🍑", "نغل", "نغولة", "نغوله", "ينغل", 
    "انيچه", "أناج", "اناج", "انيج", "أنيج", "فريخ", "فريخة", "فريخه", "فرخي","قضيب", 
    "كس", "عير", "كسمك", "كسختك", "كس امك", "طيز", "طيزك", "فرخ", "كواد", "اخلكحبة", 
    "اينيج", "بربوك", "زب", "طيزها", "عيري", "خرب الله", "العير", "بعيري", "كحبه", 
    "برابيك", "نيجني", "نيچني", "نودز", "نتلاوط", "لواط", "لوطي", "فروخ", "منيوك", 
    "انيجك", "نيجك", "كحبة", "ابن الكحبة", "ابن الكحبه", "تنيج", "اتنيج", "ينيج", "سب"
]

# إنشاء نسخة من الكلمات المحظورة بدون التكرارات الزائدة في الأحرف
normalized_banned_words = {word: re.sub(r'(.)\1+', r'\1', word) for word in banned_words}

def normalize_text(text):
    """تطبيع النص ليكون مطابقًا لقائمة الحظر"""
    text = text.lower()
    text = re.sub(r'[^أ-يa-zA-Z\s]', '', text)  # إزالة أي رموز غير الأحرف والمسافات
    replace_map = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}
    for old, new in replace_map.items():
        text = text.replace(old, new)
    text = re.sub(r'(.)\1+', r'\1', text)  # إزالة التكرارات المتتابعة في الحروف
    return text

async def is_admin(chat, user_id):
    """التحقق مما إذا كان المستخدم مشرفًا أو مالك المجموعة"""
    try:
        participant = await ABH(GetParticipantRequest(chat, user_id))
        return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
    except:
        return False

def check_message(message):
    """التحقق مما إذا كانت الرسالة تحتوي على كلمات محظورة"""
    normalized_message = normalize_text(message)
    words = normalized_message.split()
    return any(word in normalized_banned_words.values() for word in words)

@ABH.on(events.NewMessage)
async def handler_res(event):
    if event.is_group:
        message_text = event.raw_text.strip()
        user_id = event.sender_id
        chat = await event.get_chat()
        
        if check_message(message_text):  # إذا احتوت الرسالة على كلمات محظورة
            if await is_admin(chat, user_id):  # لا تفعل شيء للمشرفين، فقط احذف رسالتهم
                await event.delete()
                return
            
            # إعداد صلاحيات التقييد
            restrict_rights = ChatBannedRights(
                until_date=None,
                send_messages=True, 
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
            
            unrestrict_rights = ChatBannedRights(
                until_date=None,
                send_messages=False, 
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_links=False
            )
            
            try:
                await ABH(EditBannedRequest(chat.id, user_id, restrict_rights))  # تقييد المستخدم
                await event.delete()  # حذف رسالته
                await asyncio.sleep(20 * 60)  # الانتظار 20 دقيقة
                await ABH(EditBannedRequest(chat.id, user_id, unrestrict_rights))  # فك التقييد

            except Exception as e:
                print(f"حدث خطأ أثناء محاولة تقييد المستخدم: {e}")

ABH.run_until_disconnected()
