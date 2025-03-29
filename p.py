from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
import os, asyncio, re
from telethon import TelegramClient, events
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
banned_words = ["خرب دينه", "كسك", "كسه", "كسة", "اكحاب", "أكحاب", "زنا", "كوم بي", "كمبي", "ارقة جاي", "انيجك", "نيجك", "كحبة", "ابن الكحبة", "ابن الكحبه", "تنيج", "اتنيج", "ينيج", "طيرك", "ارقه جاي", "يموط", "تموط", "موطلي", "اموط", "بورن", "الفرخ", "الفرحْ", "تيز", "كسم", "سكسي", "كحاب", "مناويج", "منيوج", "عيورة", "عيورتكم", "انيجة", "انيچة", "انيجه", "انيچه", "أناج", "اناج", "انيج", "أنيج", "فريخ", "فريخة", "فريخه", "فرخي","قضيب", "مايا", "ماية", "مايه", "بكسمك", "بكسختك", "🍑", "نغل", "نغولة", "نغوله", "ينغل", "كس", "عير", "كسمك", "كسختك", "كس امك", "طيز", "طيزك", "فرخ", "كواد", "اخلكحبة", "اينيج", "بربوك", "زب", "طيزها", "عيري", "خرب الله", "العير", "بعيري", "كحبه", "برابيك", "سب" ,"نيجني", "نيچني", "نودز", "نتلاوط", "لواط", "لوطي", "فروخ", "منيوك"]
normalized_banned_words = {word: re.sub(r'(.)\1+', r'\1', word) for word in banned_words}
def normalize_text(text):
 text = text.lower()
 text = re.sub(r'[^أ-يa-zA-Z\s]', '', text)
 replace_map = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}
 for old, new in replace_map.items():
  text = text.replace(old, new)
 text = re.sub(r'(.)\1+', r'\1', text)
 return text
async def is_admin(chat, user_id):
 try:
  participant = await ABH(GetParticipantRequest(chat, user_id))
  return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
 except:
  return False
def check_message(message):
 normalized_message = normalize_text(message)
 words = normalized_message.split()
 return any(word in normalized_banned_words.values() for word in words)
restrict_rights = ChatBannedRights(until_date=None,send_messages=True,send_media=True,send_stickers=True,send_gifs=True,send_games=True,send_inline=True,embed_links=True)
unrestrict_rights = ChatBannedRights(until_date=None,send_messages=False,send_media=False,send_stickers=False,send_gifs=False,send_games=False,send_inline=False,embed_links=False)
warns = {}
@ABH.on(events.NewMessage)
async def handler_res(event):
 if event.is_group:
  message_text = event.raw_text.strip()
  if check_message(message_text):  
   user_id = event.sender_id
   chat = await event.get_chat()
   if await is_admin(chat, user_id):
    await event.delete()
    return
   await event.delete()
   if user_id not in warns:
    warns[user_id] = {}
   if chat.id not in warns[user_id]:
    warns[user_id][chat.id] = 0
   warns[user_id][chat.id] += 1
   if warns[user_id][chat.id] == 3:
    await ABH(EditBannedRequest(chat.id, user_id, restrict_rights))
    warns[user_id][chat.id] = 0
    await asyncio.sleep(20 * 60)
    await ABH(EditBannedRequest(chat.id, user_id, unrestrict_rights))
ABH.run_until_disconnected()
