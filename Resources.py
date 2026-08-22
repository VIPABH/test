from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest, GetFullChannelRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.messages import GetFullChatRequest
import pytz, os, json, asyncio, time, inspect, random, re
from telethon.tl.types import ChatParticipantCreator
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ReactionEmoji, User
from dateutil.relativedelta import relativedelta
from telethon.tl.types import Chat, Channel
from telethon import types, Button
from types import SimpleNamespace
from ABH import ABH, r, events
from datetime import datetime
from typing import Dict, Any
from functools import wraps
from io import BytesIO
def row_link(e, text=None):
    link = f'https://t.me/c/{str(e.chat_id).replace('-100', '')}/{e.id}'
    if text:
        return f'[{text}]({https://t.me/c/{str(e.chat_id).replace('-100', '')}/{e.id}})'
    return link
red = "danger"
green = "success"
blue = "primary"
on = 5469770542288478598
off = 5472309400536358507
def button_coloer(e, arg, name):
    return Button.inline('تعطيل' if arg else "تفعيل", data=f'toggle:{e.chat_id}:{name}', icon=on if arg else off, style='primary' if arg else 'danger')
def private(e):
    x = event_type(e)
    if e.is_private and x == 'callback':
        return True
    elif e.is_group is True:
        return True
    return False
async def edit_or_reply(event, text, chat=None, file=None):
    chat_id = chat if chat is not None else event.chat_id
    if isinstance(event, events.NewMessage.Event):
        if file:
            return await ABH.send_file(chat_id, file, caption=text, reply_to=event.id)
        return await ABH.send_message(chat_id, text, reply_to=event.id)
    elif isinstance(event, events.CallbackQuery.Event):
        try:
            if file:
                return await event.edit(file=file, text=text)
            return await event.edit(text)
        except MessageNotModifiedError:
            return None
    else:
        raise TypeError(f"Unsupported event type: {type(event)}")
def event_type(event):
    if isinstance(event, events.NewMessage.Event):
        return "NewMessage"
    elif isinstance(event, events.CallbackQuery.Event):
        return "callback"
def chunk_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]
pname = {
    'change_info': 'تغيير معلومات', 
    'delete_messages': 'حذف الرسائل', 
    'ban_users': 'حظر الاعضاء', 
    'invite_users': 'دعوه المستخدمين', 
    'pin_messages': 'تثبيت الرسائل', 
    'add_admins': 'رفع مشرفين جدد', 
    'manage_call': 'اتصال المجموعه', 
    'manage_ranks': 'تعديل الالقاب', 
    }
async def group_link(chat_id):
    try:
        chat = await ABH.get_entity(int(chat_id))
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            full_chat = await ABH(GetFullChannelRequest(chat))
        else:
            full_chat = await ABH(GetFullChatRequest(chat))                
        invite = getattr(full_chat.full_chat, 'exported_invite', None)
        link = invite.link if invite and hasattr(invite, 'link') else None
        return link            
    except Exception as e:
        return None
async def user_type(e):
    sender = await e.get_sender()
    return sender and isinstance(sender, User)
async def download_avatar(target_id_or_entity):
    target = target_id_or_entity    
    if isinstance(target, (int, str)):
        try:
            if isinstance(target, str) and (target.isdigit() or target.startswith("-")):
                target = int(target)            
            target = await ABH.get_entity(target)
        except Exception as e:
            await hint(f"فشل في استخراج الكيان من الآيدي {target_id_or_entity}: {e}")
            return None
    if not target or not getattr(target, 'photo', None):
        return None        
    try:
        photo_buffer = BytesIO()
        photo_buffer.name = "avatar.jpg"                
        await ABH.download_profile_photo(target, file=photo_buffer)        
        if photo_buffer.tell() > 0:
            photo_buffer.seek(0) 
            return photo_buffer
    except Exception as e:
        await hint(f"خطأ أثناء تنزيل الصورة: {e}")
    return None
async def extract_media_data(e):
    if not e.media: return None
    if isinstance(e.media, types.MessageMediaDocument):
        doc = e.media.document
        return {"type": "doc", "id": doc.id, "hash": doc.access_hash, "ref": doc.file_reference.hex()}
    elif isinstance(e.media, types.MessageMediaPhoto):
        photo = e.media.photo
        return {"type": "photo", "id": photo.id, "hash": photo.access_hash, "ref": photo.file_reference.hex()}
    return None
def get_years_months_days(past_date_str, date_format="%Y-%m-%d"):
    past_date = datetime.strptime(past_date_str, date_format).date()
    current_date = datetime.now().date()
    difference = relativedelta(current_date, past_date)
    years = difference.years
    months = difference.months
    days = difference.days        
    return years, months, days
async def PROFILE_SEND(e, text, buttons=None, id=None):
    id = id or e.sender_id
    l = lock(e, 'ايدي')
    input_media = None
    p = profile(id)
    if p:
        input_media = await get_input_media(p.get('media', None))
    if l and input_media:
        msg_id = getattr(e, 'message_id', None) or (e.message.id if hasattr(e, 'message') else e.id)    
        await ABH.send_file(e.chat_id, file=input_media, caption=text, buttons=buttons, reply_to=msg_id)
    else:
        await e.reply(text, buttons=buttons)
def custom_emoji(emoji):
    selected = random.choice(emoji) if isinstance(emoji, (list, tuple)) else emoji
    return f'<tg-emoji emoji-id={selected}>⬆️</tg-emoji>'
res_time = {'المعاون': 40, "المساعد": 60, 'المطور الثانوي': 120}
ban_time = {'المعاون': 7, "المساعد": 14, 'المطور الثانوي': 21}
def get_order(id_or_uid):
    target = str(id_or_uid)
    direct = r.hget('members', target)
    if direct:
        return direct
all_filters_list = []
CACHE_ENGINE = {}
RESTRICTIONS_CACHE = {}
ALIAS_CACHE_TTL = 120 
RESTRICTIONS_CACHE_TTL = 120
COMMANDS_TO_HANDLERS_MAP = {} 
step = {}
def clean_and_split_pattern(pattern_str):
    if not pattern_str:
        return []
    clean = pattern_str.strip("^$()")
    clean = re.sub(r'\[هة\]', 'ة', clean)
    clean = re.sub(r'\[ه\|ة\]', 'ة', clean)
    clean = re.sub(r'\(\.\+\)', '...', clean)
    match_group = re.search(r'\((.+?)\)', pattern_str)
    if match_group:
        prefix = pattern_str.split('(')[0].strip("^$ ")
        suffix = pattern_str.split(')')[-1].strip("^$ ")
        options = match_group.group(1).split('|')
        results = []
        for opt in options:
            opt_clean = re.sub(r'\[هة\]', 'ة', opt)
            full_command = f"{prefix} {opt_clean}".strip()
            if suffix:
                full_command = f"{full_command} {suffix}".strip()
            results.append(f"/{full_command}" if pattern_str.startswith('/') else full_command)
        return results
    elif '|' in clean:
        return [re.sub(r'\[هة\]', 'ة', opt).strip() for opt in clean.split('|')]
    else:
        return [clean]
def load_all_filters():
    global all_filters_list, COMMANDS_TO_HANDLERS_MAP
    handlers = ABH.list_event_handlers()
    all_filters_list.clear()
    COMMANDS_TO_HANDLERS_MAP.clear()
    for callback, event in handlers:
        raw_pattern = None
        if hasattr(event, 'pattern') and event.pattern:
            if hasattr(event.pattern, '__self__') and hasattr(event.pattern.__self__, 'pattern'):
                raw_pattern = event.pattern.__self__.pattern
            elif hasattr(event.pattern, 'pattern'):
                raw_pattern = event.pattern.pattern
            else:
                raw_pattern = str(event.pattern)                
        if raw_pattern:
            cleaned_words = clean_and_split_pattern(raw_pattern)
            all_filters_list.extend(cleaned_words)
            for word in cleaned_words:
                cmd_key = word[1:] if word.startswith('/') else word
                COMMANDS_TO_HANDLERS_MAP[cmd_key.strip()] = callback
    all_filters_list = list(set(all_filters_list))
@ABH.on(events.NewMessage(incoming=True))
async def execute_alias_engine(event):
    if hasattr(event,'alias_processed') and event.alias_processed:return
    if not event.raw_text:return
    if not lock(event, 'اختصارات'): return
    global CACHE_ENGINE
    chat_id=event.chat_id
    current_time=time.time()
    if chat_id not in CACHE_ENGINE or(current_time-CACHE_ENGINE[chat_id]['last_update'])>ALIAS_CACHE_TTL:
        all_aliases=r.hgetall(f"cmd:{chat_id}")
        if not all_aliases:CACHE_ENGINE[chat_id]={'aliases':{},'last_update':current_time}
        else:
            processed_data={(k.decode('utf-8') if isinstance(k,bytes) else str(k)).strip():(v.decode('utf-8') if isinstance(v,bytes) else str(v)).strip() for k,v in all_aliases.items()}
            CACHE_ENGINE[chat_id]={'aliases':processed_data,'last_update':current_time}
    cache=CACHE_ENGINE[chat_id]
    if not cache['aliases']:return
    text=event.raw_text.strip()
    if text in cache['aliases']:
        real_cmd=cache['aliases'][text]
        event.alias_processed=True
        event.message.message=real_cmd
        for handler,event_builder in ABH.list_event_handlers():
            if handler==execute_alias_engine:continue
            if isinstance(event_builder,events.NewMessage) and hasattr(event_builder,'pattern') and event_builder.pattern:
                pat=event_builder.pattern
                if callable(pat):
                    match=pat(real_cmd)
                    if match:
                        event.pattern_match=match
                        await handler(event)
                else:
                    match=re.match(pat,real_cmd)
                    if match:
                        event.pattern_match=match
                        await handler(event)
        raise events.StopPropagation
@ABH.on(events.NewMessage(incoming=True))
async def check_command_restrictions(event):
    if not event.raw_text or event.is_private:return
    if not lock(event, 'اوامر المقيده'): return
    global RESTRICTIONS_CACHE, COMMANDS_TO_HANDLERS_MAP
    chat_id = event.chat_id
    current_time = time.time()
    text = event.raw_text.strip()
    if chat_id not in RESTRICTIONS_CACHE or (current_time - RESTRICTIONS_CACHE[chat_id]['last_update']) > RESTRICTIONS_CACHE_TTL:
        res_data = r.hgetall(f"group:{chat_id}:restricted_commands")
        if not res_data:
            RESTRICTIONS_CACHE[chat_id] = {'commands': {}, 'last_update': current_time}
        else:
            processed_res = {
                k.decode('utf-8').strip() if isinstance(k, bytes) else str(k).strip(): 
                v.decode('utf-8').strip() if isinstance(v, bytes) else str(v).strip() 
                for k, v in res_data.items()
            }
            RESTRICTIONS_CACHE[chat_id] = {'commands': processed_res, 'last_update': current_time}
    group_restrictions = RESTRICTIONS_CACHE.get(chat_id, {}).get('commands', {})
    if not group_restrictions:
        return 
    clean_text = text
    if text.startswith(('/', '.', '!')):
        clean_text = text[1:]
    clean_text = re.sub(r'@\w+\b', '', clean_text).strip()    
    words = clean_text.split()
    if not words:
        return
    for i in range(min(3, len(words)), 0, -1):
        cmd_check = " ".join(words[:i]).strip()
        if cmd_check in group_restrictions:
            await _apply_restriction_logic(event, cmd_check, group_restrictions[cmd_check])
            return
        if cmd_check in COMMANDS_TO_HANDLERS_MAP:
            target_handler = COMMANDS_TO_HANDLERS_MAP[cmd_check]
            all_aliases_of_this_handler = [
                k for k, v in COMMANDS_TO_HANDLERS_MAP.items() if v == target_handler
            ]
            for alias in all_aliases_of_this_handler:
                if alias in group_restrictions:
                    target_rank = group_restrictions[alias]
                    await _apply_restriction_logic(event, alias, target_rank)
                    return
            break
async def _apply_restriction_logic(event, alias_name, target_rank):
    user_rank = await auth(event)
    if user_rank != target_rank:
        if not authers(user_rank, target_rank): 
            await event.reply(
                f"⚠️ عذرا بس ماتكدر تستخدم امر ( {event.text} ) الامر خاص ل {target_rank if target_rank == 'المالك' else target_rank + 'وفوك'}"
            )
            raise events.StopPropagation
def timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()        
        await func(*args, **kwargs)        
        end_time = time.perf_counter()
        duration = end_time - start_time
        msg = f"─── الدالة: {func.__name__}\n ─── استغرقت: {duration:.4f} ثانية"
        return await hint(msg)
    return wrapper
def dev(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        if event.sender_id == wfffp:
            return await func(event, *args, **kwargs)
        else:
            return
    return wrapper
def profile(user_id):
    data = r.get(f"user:{user_id}")
    return json.loads(data) if data else None
def save_user(user_id, data):
    """حفظ بيانات المستخدم (JSON)"""
    r.set(f"user:{user_id}", json.dumps(data, ensure_ascii=False))
async def get_input_media(media_data):
    if not media_data or not isinstance(media_data, dict):
        return None
    m_id = int(media_data['id'])
    m_hash = int(media_data['hash'])
    m_ref = bytes.fromhex(media_data['ref'])    
    if media_data['type'] == "doc":
        return types.InputDocument(id=m_id, access_hash=m_hash, file_reference=m_ref)
    return types.InputPhoto(id=m_id, access_hash=m_hash, file_reference=m_ref)
async def extract_media_data(e):
    if not e.media: return None
    if isinstance(e.media, types.MessageMediaDocument):
        doc = e.media.document
        return {"type": "doc", "id": doc.id, "hash": doc.access_hash, "ref": doc.file_reference.hex()}
    elif isinstance(e.media, types.MessageMediaPhoto):
        photo = e.media.photo
        return {"type": "photo", "id": photo.id, "hash": photo.access_hash, "ref": photo.file_reference.hex()}
    return None
async def get_profile_photo(id, user=None):
    photos = []
    try:
        user = user if user else await ABH.get_entity(id)
        photos = await ABH.get_profile_photos(user, limit=1)
        if photos:
            return photos[0]
        else:
            return None
    except:
            return None
async def bot():
    'id, username, first_name, last_name, full_name, is_bot, photo_id'
    key = "bot:info"
    data = r.get(key)
    if data:
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    me = await ABH.get_me()
    full_name = f"{me.first_name or ''} {me.last_name or ''}"
    bot_data = {
        "id": me.id,
        "username": me.username,
        "first_name": me.first_name,
        "last_name": me.last_name,
        "full_name": full_name,
        "is_bot": me.bot,
        "photo_id": None
    }
    photos = await ABH.get_profile_photos(me.id, limit=1)
    if photos:
        bot_data["photo_id"] = photos[0].id    
    r.set(key, json.dumps(bot_data))
    return SimpleNamespace(**bot_data)
async def mentions(users: list, text='↔'):
    mention = []
    users_to_fetch = [] 
    cached_names = {}   
    for user_id in users:
        uid = int(user_id)
        profilename = profile(uid) 
        if profilename:
            cached_names[uid] = profilename.get('name', 'حساب محذوف')
        else:
            users_to_fetch.append(uid)
    fetched_users = {}
    if users_to_fetch:
        try:
            full_users = await ABH.get_entity(users_to_fetch)
            if not isinstance(full_users, list):
                full_users = [full_users]
            for u in full_users:
                if u:
                    fetched_users[u.id] = getattr(u, 'first_name', 'حساب محذوف')
        except Exception as e:
            print(f"Error fetching entities: {e}")
    for user_id in users:
        uid = int(user_id)        
        if uid in cached_names:
            name = cached_names[uid]
        elif uid in fetched_users:
            name = fetched_users[uid]
        else:
            name = "حساب محذوف"
        mention.append(f"{unicode}[{name}](tg://user?id={uid}) {unicode}{text} {unicode}`{uid}`")
    return mention
mem = [
    'ميعرف', 'صباح الخير', 'لا تتماده', 'يله شنسوي', 'ههههه', 
    'استرجل', 'man up', 'واستيد', 'wasted', 'زعطوط', 'مخبل', 
    'عالم موازي', 'هايشكل', 'مواقع تعليم اللغه العربية',
    'متاقلم', 'مشاجره', 'مشاجرة', 'توحد', 'تنمر', 'تخيل',
    'قريده', 'مستغرب', 'يصبرني', 'تاقلم', 'اتاقلم',
    'لتعيدها', 'نو', 'نو بليز', 'الاملاء', 'اسكت',
    'ماعرف', 'خسيس', 'حصفور', 'قطريق', 'قواصر', 
    'فكاهي', 'القردقاله', 'قطاطس', 'كلكبوت',
    'ارعن', 'جذاب', 'كذبه', 'جذبه', 'دروح']
count = [
    'عدد تفاعل', 
    'عدد المتفاعلين',
    'توب اليومي',
    'توب الاسبوعي',
    'رسائلي',
    'رسائله',
]
games = [
    'تعيين رقم', 
    'حذف رقم',
    "اعلام",
    'رياضيات', 
    'ارقام',
    'محيبس',
    'اكس او',
    'اسرع',
    "اسئلة دينية",
    "اسئلة رياضية",
    "حجرة",
    "اسرع",
    "غموض",
    "كتويت",
    ]
group = [
    "كشف القيود",
    "عرض الاعدادات",
    "كم حرف",
    "كم كلمة",
    "ايديي",
    'بروفايلي',
    'ايديه',
    "بروفايله",
    "ترتيبي",
    "ترتيبه",
    "ترتيب 1",
    "معلوماتي",
    "احصائياتي",
    "معلوماته",
    'احصائياته',
    "اوامر القفل والفتح",
    'ال+اسم الامر تعطيل | تفعيل',
    "توب الحماية",
    'مخفي احميني',
    "رتبتي",
    'رتبته',
    "مخفي اختار",
    'سرقة',
    'خمط',
    'تداول',
    'مضاربة',
    'ازعاج',
    'مواعيد',
    'كم باقي',
    'كشف ايدي',
    "ترجمة",
    'صلاحياته',
    'لقبه',
    'تاريخ انضمامي',
    'انضمامي',
    'تاريخ انضمامه',
    'اقرا 511',
]
guard = [
"المحظورين عام",
"الغاء المحظور عام",
"حذف المحظورين عام",
"الغاء حظر عام",
"حظر عام",
'مخفي امنع',
'حذف قائمة المنع',
"الغاء منع",
"قائمة المنع",
"الممنوعات",
"المقيدين عام",
"مسح المقيدين عام",
"الغاء تقييد عام",
"تقييد عام",
"توب",
"توب التقييد",
"توب التحذير",
"توب المقيدين",
"توب المحذرين",
"التعديل",
'تعيين قناة',
"حذف القناة",
'عرض القناة',
"تحذيراته",
'تحذيراتي',
"تصفير التذيرات",
'تحذير',
]
other = [
    'رسائل المجموعة',
    'زر',
    'كشف الهمسة',
    'اسمي',
    'اسمه',
    'رقمة',
    'رقمي',
    'يوزراتي',
    'يوزراته',
    'يوزري',
    'يوزره',
    'قران',
    'قرآن',
    'سورة (اسم السورة)',
    'مخفي + نص السؤال',
    'اوامر الحظ',
    'لطميه',
    'لطميات',
    "احسب 223*77",
    'ميم',
    'كشف رابط',
    "سكرين",
    'اهمس',
    'همساتي',
    'همساته',
    'حسابي', 
    "حسابه",
]
addanddel = [
    "ترقية",
    "تعديل صلاحياته",
    "تنزيل مشرف",
    "رفع مطور ثانوي",
    "تنزيل مطور ثانوي",
    'رفع مساعد',
    'تنزيل مساعد',
    "رفع معاون",
    "تنزيل معاون",
    "رفع منظف",
    "تنزيل منظف",
    "تغيير لقبي",
    "عرض الرتب",
    "المطورين الثانويين",
    'حذف المطورين الثانويين',
    "المساعدين",
    'حذف المساعدين',
    "المعاونين",
    'حذف المعاونين',
    "المنظفين",
    'حذف المنظفين',
    "الرتب"
]
other_lock = ['الصور', 'المتحركات', 'الفويس نوت', 'الفيديوهات', 'الستيكرات', 'الفويسات', 'الملفات', 'المواقع', 'الاستفتاءات']
bannedactions = {
    'يوتيوب': 'المعاون',
    'ايدي': 'المعاون',
    'تقييد': 'المساعد',
    'ردود': 'المعاون',
    'تنظيف': 'المعاون',
    'تحذير': 'المعاون', 
    'منع': 'المساعد', 
    'رفع': 'المساعد', 
    'العاب': 'المعاون', 
    'همسة': 'المساعد',
    'توب': 'المساعد',
    'ترقية وصلاحياتها': 'المالك',
    'اوامر المقيده': 'المالك',
    'اختصارات': 'المساعد',
    'اوامر العامة': 'المطور الثانوي',
    'تعديل': 'المطور الثانوي',
    'ترقية': 'المطور الثانوي',
    'بوتات المضافة': 'المساعد',
    'ميم': 'المعاون',
}
actions = [
    'يوتيوب', 'تقييد', 'ردود', 'تنظيف', 'تحذير', 'ترقية وصلاحياتها',
    'منع', 'العاب', 'همسة', 'ترقية', 'رفع', 'بوتات المضافة', 'اوامر المقيده',
    'ايدي', 'توب', 'تعديل', 'اوامر العامة', 'ميم', 'اختصارات'
]
lockANDunlock = 'اوامر **الفتح والتعطيل** كآلاتي\n'
lockANDunlock += '\n'.join([f'{i}- `ال{action} تفعيل` | `ال{action} تعطيل`' for i, action in enumerate(actions, 1)])
allcommands = {
    'الرسائل': count,
    'الالعاب': games,
    'المجموعه': group,
    'الحماية': guard,
    'اخرى': other,
    'الرفع والتنزيل': addanddel,
    'الرفع': addanddel,
    'الادارة': addanddel,
    'الفتح والتعطيل': lockANDunlock,
    'الميم': mem
}
@ABH.on(events.NewMessage(pattern=r'^الاوامر$'))
async def all_commands(event):
    if not event.is_group:
        return
    msg = "📊 **اوامر البوت:**\n\n"
    for num, (category, _) in enumerate(allcommands.items(), start=1):
        msg += f"**{num}- `اوامر {category}`:**\n"
    await event.reply(msg)
@ABH.on(events.NewMessage(pattern='^اوامر (الرفع|الادار[هة]|الرفع والتنزيل|الرسائل|الالعاب|المجموع[هة]|الحماي[هة]|الفتح والتعطيل|الميم|اخرى)$'))
async def commands(event):
    if not event.is_group:return
    if event.text == 'اوامر الفتح والتعطيل':
        return await event.reply(lockANDunlock)
    category = event.pattern_match.group(1)
    cmds_list = allcommands.get(category, [])
    command = f"**{event.text}**\n\n" + "\n".join(f"{i} - `{cmd}` " for i, cmd in enumerate(cmds_list, start=1))
    await event.reply(command)
unicode = "\u200f"
def lock(e, type):
    lock_key = f"lock:{e.chat_id}:{type}"
    return r.get(lock_key) == "True"
wfffp = 1910015590
@ABH.on(events.NewMessage(pattern='رفع مطور اساسي|نقل ملكية البوت|رتبتي وين مخفي؟$'))
async def tansferbotowner(e):
    global wfffp
    if e.sender_id != wfffp: return await react(e, '🤣')
    r = await e.get_reply_message()
    if not r:
        return await e.reply('عذرا بس ل خطوره الامر لازم تشغله بالرد')
    wfffp = r.sender_id
    m = await ment(wfffp)
    b = await bot()
    await e.reply(f'تم نقل ملكية البوت {b.full_name} الى المستخدم {m}')
    try:
        await ABH.send_message(wfffp, 'مرحبا عزيزي {} انت حاليا المطور الاساسي الجديد واني راح اساعدك , انت حاليا المالك مالتي'.format(m))
    except:
        pass
    if e.text == 'نقل ملكية البوت': return
    await asyncio.sleep(60)
    await ABH.send_message(wfffp, 'هههههههه ضحكنه عليك يالغالي , رجعت ابن هاش مطور و نزلتك')
    wfffp = 1910015590
    await e.respond(file='https://t.me/recoursec/30', message='تم ارجاع الملكية الى المطور الاصلي ابن هاشم السبب \n لان واحد عراق', reply_to=e.id)
    if e.text == 'رتبتي وين مخفي؟' and e.sender_id == 1910015590:
        wfffp = 1910015590
        return await chs(e, 'اعذرنه يالامير رجعناك اساسي')
async def userstates(chat_id: int, user_id: int) -> str:
    try:
        participant = await ABH(GetParticipantRequest(
            channel=chat_id,
            participant=user_id
        ))
        p = participant.participant
        if isinstance(p, types.ChannelParticipantCreator):
            return "مالك"
        if isinstance(p, types.ChannelParticipantBanned):
            return "محظور" if p.left else "مقيّد"
        if isinstance(p, types.ChannelParticipantAdmin):
            return "مشرف"
        if isinstance(p, types.ChannelParticipant):
            return "عضو"
        return "غير معروف"
    except UserNotParticipantError:
        return "مغادر المجموعة"
    except Exception as E:
        await hint("userstates +++ " + str(E))
def extractfree(text):
    user = None
    user_id = None
    duration = None
    user_match = re.search(r'@\w+', text)
    if user_match:
        user = user_match.group(0)
    id_match = re.search(r'(?:\s+|^)(\d{5,10})(?:\s+|$)', text)
    if id_match:
        user_id = id_match.group(1)
    times = re.findall(r'(?:\s+|^)(\d{1,3})(?:\s+|$)', text)
    for t in times:
        if 1 <= int(t) <= 9999: 
            duration = t
            break
    return user, user_id, duration
def extract(text):
    match = re.search(r"(@\w+|\d+)(?:\s+(\d+))?", text)
    if match:
        user = match.group(1)
        number = match.group(2)
        return user, number
    return None, None
def special(e):
    id = e.sender_id
    return id != wfffp
ranks_weights = {
    'المطور الاساسي': 1, 
    'الرقيب هاشم': 2,
    'المالك': 3, 
    'المطور ثانوي': 4,
    'المساعد': 5, 
    'المعاون': 6,
}
# ranks_weights = {
#     'المطور الاساسي': 1, 
#     'المالك': 2, 
#     'المطور ثانوي': 3,
#     'المساعد': 4, 
#     'المعاون': 5,
# }
def authers(arg1, arg2):
    a1 = ranks_weights.get(arg1, 100)
    a2 = ranks_weights.get(arg2, None)
    if not a2:
        return True
    return a1 < a2
b = Button.inline("اضغط هنا لعرضها كتابة", data='moneymuch')
n1 = """🟥🟥🟥🟥🟥🟥🟥🟥🟥
🟥⬜⬜⬜⬜⬜⬜⬜🟥
🟥⬜⬛⬜⬛⬛⬛⬜🟥
🟥⬜️⬛️⬜️⬛️⬜️⬜️⬜️🟥
🟥⬜️⬛️⬛️⬛️⬛️⬛️⬜️🟥
🟥⬜️⬜️⬜️⬛️⬜️⬛️⬜️🟥
🟥⬜️⬛️⬛️⬛️⬜️⬛️⬜️🟥
🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️🟥
🟥🟥🟥🟥🟥🟥🟥🟥🟥
"""
n2 = """⠙⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢹⠿⣿⣿⣿⣿⣿
⣷⣶⡀⠿⠿⣿⣿⣿⣿⣿⣿⡇⠐⠂⢒⡢⠀⣿⣿⣿
⣿⣿⣿⣆⠀⠈⢻⣿⣿⣿⣿⣿⡆⢈⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣷⣄⠀⠙⠻⢻⢿⣿⠷⢠⢽⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣧⡀⠁⠀⢘⣱⣍⠿⣾⢿⣿⢿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠀⠀⢉⢷⣌⠳⣿⣽⣛⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠋⠽⠶⡌⣿⣻⣀
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣠⡀⠀⠀⠀⠐⠇⢿⣿⣿
⠿⠿⠿⠿⠿⠿⠿⠿⠏⠁⠀⠈⠀⠅⠶⠲⠶⠆⠔⠿"""
n3 = """⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠟⠛⠉⣩⣍⠉⠛⠻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⠋⠀⠀⣠⣾⣿⠟⠁⠀⠀⠀⠙⣿⣿⣿⣿
⣿⣿⣿⠁⠀⠀⢾⣿⣟⠁⠀⣠⣾⣷⣄⠀⠘⣿⣿⣿
⣿⣿⡇⣠⣦⡀⠀⠙⢿⣷⣾⡿⠋⠻⣿⣷⣄⢸⣿⣿
⣿⣿⡇⠙⢿⣿⣦⣠⣾⡿⢿⣷⣄⠀⠈⠻⠋⢸⣿⣿
⣿⣿⣿⡀⠀⠙⢿⡿⠋⠀⢀⣽⣿⡷⠀⠀⢠⣿⣿⣿
⣿⣿⣿⣿⣄⠀⠀⠀⢀⣴⣿⡿⠋⠀⠀⣠⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣦⣤⣀⣙⣋⣀⣤⣴⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"""
def gettime(start_time, duration=30*60):
    end_time = start_time + duration
    now = int(time.time())
    remaining = max(0, end_time - now)
    return remaining, end_time
def scan(filename):
    create(filename)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
def قفل(x):
    return f"عذرا بس الامر ل {x}"
ignore_phrases = [
    "مخفي احذف",
    "مخفي احميني",
    "مخفي اعفطلة",
    "مخفي اعفطله",
    "مخفي قيده",
    "مخفي قيدة",
    "مخفي طكة زيج",
    "مخفي اطلع",
    "مخفي غادر",
    "مخفي نزلني",
    "مخفي نزلة",
    "مخفي نزله",
    "مخفي اختار"
]
async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False
async def to(e, args=1, text=None, id=None):
    'target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)'
    try:
        reply = await e.get_reply_message()
        if reply:
            return reply
        args = text if text else e.pattern_match.group(int(args))
        target = args if args else id
        if target and target.isdigit():
            return await ABH.get_entity(int(target))
        if target:
            if target.startswith('@'):
                target = target[1:]
            elif target.startswith('https://t.me/'):
                target = target.replace('https://t.me/', '')
            entity = await ABH.get_entity(target)
            return entity
    except:
        return None
ADMIN_CACHE = {}
CACHE_TIME = 120
async def is_admin(chat_id, user_id):
    cache_key = f"{chat_id}:{user_id}"
    now = time.time()    
    if cache_key in ADMIN_CACHE:
        is_admin, timestamp = ADMIN_CACHE[cache_key]
        if now - timestamp < CACHE_TIME:
            return is_admin
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        is_admin = isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
    except:
        is_admin = False    
    ADMIN_CACHE[cache_key] = (is_admin, now)
    return is_admin
AUTH_CACHE = {}
CACHE_TIME = 5 
def set_user_rank(chat_id, user_id, rank_name):
    r.hset(f"ranks:{chat_id}", str(user_id), rank_name)
def get_all_group_data(chat_id):
    return r.hgetall(f"ranks:{chat_id}")
def remove_user(chat_id, user_id):
    r.hdel(f"ranks:{chat_id}", str(user_id)) 
def get_user_rank(chat_id, user_id):
    rank = r.hget(f"ranks:{chat_id}", str(user_id))    
    return rank if rank else None
async def auth(event, x=False, to=None, chat=None):
    chat_id = chat if chat else event.chat_id
    if to:
        user_id = to
    elif x:
        reply_msg = await event.get_reply_message()
        if not reply_msg:
            return None
        user_id = reply_msg.sender_id
    else:
        user_id = event.sender_id            
    if not user_id:
        return None
    user_id_str = str(user_id)
    if user_id == wfffp:
        return "المطور الاساسي"
    elif user_id == 7400171284:
        return 'الرقيب هاشم'
    if chat_id in AUTH_CACHE:
        if user_id_str in AUTH_CACHE[chat_id]:
            return AUTH_CACHE[chat_id][user_id_str]
    if await is_owner(chat_id, user_id):
        if chat_id not in AUTH_CACHE:
            AUTH_CACHE[chat_id] = {}
        AUTH_CACHE[chat_id][user_id_str] = "المالك"
        return "المالك"
    redis_key = f"ranks:{chat_id}"    
    user_rank = r.hget(redis_key, user_id_str)    
    if user_rank:
        admin = await is_admin(chat_id, user_id)        
        if not admin:
            r.hdel(redis_key, user_id_str)
            remove_user(chat_id, user_id)
            m = await ment(user_id)
            await event.reply(f"تم حذف {m} من {user_rank} لعدم وجود صلاحيات إدارية")
            return None
        return 'ال'+ user_rank
    return None
AUTH_FILE = 'assistant.json'
if not os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, 'w') as f:
        json.dump({}, f)
def load_auth():
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)
def save_auth(data):
    with open(AUTH_FILE, 'w') as f:
        json.dump(data, f)
def is_assistant(chat_id, user_id):
    data = load_auth()
    assistants = data.get(str(chat_id), [])
    return user_id in assistants
def add_warning(user_id: int, chat_id: int) -> int:
    key = f"warns:{chat_id}:{user_id}"
    current_warns = r.incr(key)
    if current_warns >= 3:
        r.delete(key)
        current_warns = 3
    return current_warns
def del_warning(user_id: int, chat_id: int) -> int:
    key = f"warns:{chat_id}:{user_id}"
    current = int(r.get(key) or 0)
    if current > 0:
        current = r.decr(key)
        return current
    return 0
def zerowarn(user_id: int, chat_id: int) -> int:
    key = f"warns:{chat_id}:{user_id}"
    if r.exists(key):
        r.delete(key)
    return 0
def count_warnings(user_id: int, chat_id: int) -> int:
    key = f"warns:{chat_id}:{user_id}"
    if r.exists(key):
        count = int(r.get(key))
        if not count or count == 0:
            r.delete(key)
            return 0
        return count
    return None
async def send(e, m, chat=None):
    c = chat if chat else e.chat_id
    l = LC(str(c))
    if not l:
        return
    p = profile(e.sender_id)
    if p and p.get('media', None):
        input_media = await get_input_media(p.get('media'))
        await ABH.send_file(entity=l, file=input_media, caption=m)
    else:
        await ABH.send_message(entity=l, message=m)
def create(filename):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
def save_json(filename, data):
    str_data = {str(k): v for k, v in data.items()}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(str_data, f, ensure_ascii=False, indent=4)
async def res(المصدر=None, stop=False, t=20*60, id=None):
    if isinstance(المصدر, str) and ":" in المصدر:
        parts = المصدر.split(":")
        chat_id, user_id = str(parts[0]), str(parts[1])
    else:
        if id:
            user_id = id
        else:
            user_id = المصدر.sender_id
        chat_id = str(المصدر.chat_id)
    end_time = int(time.time()) + (t or 20)    
    r.hset(chat_id, user_id, end_time)
    admin = await is_admin(chat_id, user_id)
    if not admin:
        now = int(time.time())
        rights = ChatBannedRights(
            until_date=now + (t or 20),
            send_messages=True
        )
        await ABH(EditBannedRequest(channel=int(chat_id), participant=int(user_id), banned_rights=rights))
        return
def delres(chat_id=None, user_id=None):
    chat_str = str(chat_id)
    user_str = str(user_id)    
    if r.hexists(chat_str, user_str):
        r.hdel(chat_str, user_str)
        if r.hlen(chat_str) == 0:
            r.delete(chat_str)
        return True
    return False
async def info(e, msg_type):
    chat = str(e.chat_id)
    user_id = str(e.sender_id)
    key = f"userstats:{chat}:{user_id}"
    if msg_type is None:
        data = r.hgetall(key)
        if not data:
            return {
                "الرسائل": 0,
                "الصور": 0,
                "المتحركات": 0,
                "الفويس نوت": 0,
                "الفيديوهات": 0,
                "الستيكرات": 0,
                "الفويسات": 0,
                "الصوتيات": 0,
                "الملفات": 0,
                "المواقع": 0,
                "الاستفتاءات": 0
            }
        return {k: int(v) for k, v in data.items()}
    r.hincrby(key, msg_type, 1)
    if msg_type != "الرسائل":
        r.hincrby(key, "الرسائل", 1)
    data = r.hgetall(key)
    return {k: int(v) for k, v in data.items()}
def ads(group_id, user_id):
    r.sadd(f"whitelist:{group_id}", str(user_id))
def lw(e):
    return r.sismember(f"whitelist:{e.chat_id}", str(e.sender_id))
async def configc(group_id: int, hint_cid=None) -> None:
    key = f"config:{group_id}"
    if hint_cid is None:
        r.delete(key)
        return
    r.set(key, int(hint_cid))
def LC(group_id):
    key = f"config:{group_id}"
    value = r.get(key)
    if value is not None:
        return int(value)
    return None
async def link(e, text=False):
    chat_id = e.chat_id    
    msg_id = getattr(e, 'message_id', None) or (e.message.id if hasattr(e, 'message') else e.id)    
    c = str(chat_id).replace('-100', '')
    link_url = f'https://t.me/c/{c}/{msg_id}'
    if text:
        return link_url    
    chat = await e.get_chat()
    name = getattr(chat, "title", "المحادثة")
    return f"[{name}]({link_url})"
async def usernames(user_object):
    usernames_list = []    
    if getattr(user_object, "usernames", None):
        for u in user_object.usernames:
            if getattr(u, "username", None):
                usernames_list.append(f"@{u.username}")    
    if getattr(user_object, "username", None):
        usernames_list.insert(0, f"@{user_object.username}")    
    usernames_list = list(dict.fromkeys(usernames_list))
    if usernames_list:
        return ", ".join(usernames_list)
    return None
async def username(event, x=None):
    if x and x is not True:
        try:
            entity = await event.client.get_entity(x)
            if entity.username:
                return f"@{entity.username}"
            return str(entity.id) 
        except:
            return "مستخدم غير معروف"
    if x is True:
        r = await event.get_reply_message()
        if not r or not r.sender:
            return 'مالي خلك روح جيبه انت'
        if getattr(r.sender, 'username', None):
            return f"@{r.sender.username}"
        return str(r.sender_id)
    sender = await event.get_sender()
    if sender and getattr(sender, 'username', None):
        return f"@{sender.username}"    
    if hasattr(sender, "usernames") and sender.usernames:
        for u in sender.usernames:
            if u.active:
                return f"@{u.username}"
    return "لا يوجد يوزر"
async def try_forward(event, r=None, chat=None, id=None, to=None, drop_author=None):
    gidvar = LC(event.chat_id)
    if id:
        msg = id
    elif r:
        msg = r.id
    else:
        msg = event.id
    from_peer = chat if chat else event.chat_id
    target_chat = to if to else gidvar
    if not target_chat: 
        return False        
    try:
        await ABH.forward_messages(
            entity=int(target_chat),
            messages=int(msg),
            from_peer=int(from_peer),
            drop_author=drop_author
        )
        return True
    except Exception as e:
        return False
developers = {}
def delsave(dev_id=None, filename="secondary_devs.json"):
    if filename is None:
        return
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    if dev_id is None:
        return data
    if ":" not in dev_id:
        return data
    parts = dev_id.split(":", 1)
    if len(parts) != 2:
        return data
    chat_id, dev_id_num = parts
    if chat_id in data and dev_id_num in data[chat_id]:
        data[chat_id].remove(dev_id_num)
        if not data[chat_id]:
            del data[chat_id]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
def save(dev_id=None, filename="secondary_devs.json"):
    if filename is None:
        return
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    if dev_id is None:
        return data
    if ":" not in dev_id:
        return data
    parts = dev_id.split(":", 1)
    if len(parts) != 2:
        return data
    chat_id, dev_id_num = parts
    if chat_id not in data:
        data[chat_id] = []
    if dev_id_num not in data[chat_id]:
        data[chat_id].append(dev_id_num)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
async def react(event, x):
    msg_id = getattr(event, 'id', None) or getattr(event.message, 'id', None)
    chat_id = getattr(event, 'chat_id', None) or getattr(event.message, 'chat_id', None)
    if not msg_id or not chat_id:
        return
    try:
        await ABH(SendReactionRequest(
            peer=chat_id,
            msg_id=msg_id,
            reaction=[ReactionEmoji(emoticon=x)],
            big=False))
    except Exception as e:
        return
def adj(filename: str, data: Dict[str, Any]) -> bool:
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, dict):
                    existing_data = {}
            except (json.JSONDecodeError, ValueError):
                existing_data = {}
        existing_data.update(data)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ خطأ أثناء تعديل الملف {filename}: {e}")
        return False
async def can_add_admins(chat, user_id):
    try:
        result = await ABH(GetParticipantRequest(
            channel=chat,
            participant=user_id
        ))
        role = result.participant
        if isinstance(role, ChannelParticipantCreator):
            return True
        if isinstance(role, ChannelParticipantAdmin):
            rights = role.admin_rights
            if rights and rights.add_admins:
                return True
        return False
    except:
        return False
async def can_ban_users(chat, user_id):
    try:
        result = await ABH(GetParticipantRequest(
            channel=chat,
            participant=user_id
        ))
        role = result.participant
        if isinstance(role, ChannelParticipantCreator):
            return True
        if isinstance(role, ChannelParticipantAdmin):
            rights = role.admin_rights
            if rights and rights.ban_users:
                return True
        return False
    except:
        return False
async def get_owner(event):
    try:
        chat = await event.get_chat()
        if isinstance(chat, Chat):
            full = await ABH(GetFullChatRequest(chat.id))
            for p in full.full_chat.participants.participants:
                if isinstance(p, ChannelParticipantCreator):
                    return await ABH.get_entity(p.user_id)
        elif isinstance(chat, Channel):
            async for user in ABH.iter_participants(chat, filter=ChannelParticipantsAdmins):
                if isinstance(user.participant, ChannelParticipantCreator):
                    return user
    except Exception as e:
        print(f"[get_owner error]: {e}")
        return None
    return None
timezone = pytz.timezone('Asia/Baghdad')
wfffp = 1910015590
async def hint(e):
    frame = inspect.currentframe().f_back
    try:
        filename = os.path.basename(frame.f_code.co_filename)
        line = frame.f_lineno
        func_name = frame.f_code.co_name        
        msg = (
            f"📍 **تفاصيل مكان الاستدعاء:**\n"
            f"• الملف: `{filename}`\n"
            f"• الدالة المستدعية: `{func_name}`\n"
            f"• رقم السطر: `{line}`\n"
        )
        await ABH.send_message(wfffp, msg)
        await ABH.send_message(wfffp, str(e))    
    finally:
        del frame
mentions_dict = {}
async def mention(event):
    user_id = event.sender_id
    if user_id in mentions_dict:
        return mentions_dict[user_id]
    user_data = profile(user_id)
    name = None
    if user_data and isinstance(user_data, dict):
        name = user_data.get('name')    
    if not name:
        sender = await event.get_sender()
        name = getattr(sender, 'first_name', 'مستخدم') or 'مستخدم'
    if user_id not in mentions_dict:
        mentions_dict[user_id] = f"[{name}](tg://user?id={user_id})"
    return f"[{name}](tg://user?id={user_id})"
async def ment(entity, text=None):
    try:
        user_id = None
        name = None
        if isinstance(entity, int):
            user_id = entity
        elif isinstance(entity, str) and entity.isdigit():
            user_id = int(entity)
        elif hasattr(entity, 'sender_id'): 
            user_id = entity.sender_id
        elif hasattr(entity, 'id'): 
            user_id = entity.id
        if not user_id:
            return "غير معروف"
        if user_id in mentions_dict:
            return mentions_dict[user_id]
        user_data = profile(user_id)
        if user_data:
            name = user_data.get('name') if isinstance(user_data, dict) else getattr(user_data, 'name', None)
        if not name:
            if not hasattr(entity, 'first_name') or (hasattr(entity, 'id') and entity.id != user_id):
                entity = await ABH.get_entity(user_id)
            name = getattr(entity, 'first_name', 'مستخدم') or 'مستخدم'
        if user_id not in mentions_dict:
            mentions_dict[user_id] = f"[{name}](tg://user?id={user_id})"
            if text: 
                return name
        return f"[{name}](tg://user?id={user_id})"
    except Exception as e:
        return "غير معروف"
football = [
        {
            "answer": "الميعوف",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/c/2219196756/21013"
        },
        {
            "answer": "سالم الدوسري",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/54"
        },
        {
            "answer": "العويس",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/56"
        },
        {
            "answer": "علي البليهي",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/58"
        },
        {
            "answer": "جحفلي",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/60"
        },
        {
            "answer": "الشلهوب",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/62"
        },
        {
            "answer": "محمد البريك",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/64"
        },
        {
            "answer": "سعود",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/66"
        },
        {
            "answer": "ياسر الشهراني",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/70"
        },
        {
            "answer": ["كريستيانو رونالدو", 'رونالدو'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/72"
        },
        {
            "answer": ["امبابي", 'مبابي', 'كيليان مبابي'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/74"
        },
        {
            "answer": "مودريتش",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/76"
        },
        {
            "answer": ["بنزيما", "كريم بنزيما"],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/78"
        },
        {
            "answer": "نيمار",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/80"
        },
        {
            "answer": ["ميسي", 'ليونيل ميسي'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/82"
        },
        {
            "answer": ["راموس", 'سيرخيو راموس', 'سيرخيوس راموس'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/84"
        },
        {
            "answer": "اشرف حكيمي",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/86"
        },
        {
            "answer": "ماركينيوس",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/88"
        },
        {
            "answer": "محمد صلاح",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/90"
        },
        {
            "answer": "هازارد",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/92"
        },
        {
            "answer": "مالديني",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/94"
        },
        {
            "answer": "انيستا",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/96"
        },
        {
            "answer": "تشافي",
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/98"
        },
        {
            "answer": ["بيكيه", 'جيرارد بيكيه'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/100"
        },
        {
            "answer": ["بيل", 'غارث بيل'],
            "caption": "شنو اسم الاعب ؟",
            "photo": "https://t.me/LANBOT2/102"
        },
        {
            "answer": "1995",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/104"
        },
        {
            "answer": "1997",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/106"
        },
        {
            "answer": "1998",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/108"
        },
        {
            "answer": "1999",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/110"
        },
        {
            "answer": "2002",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/112"
        },
        {
            "answer": "2005",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/114"
        },
        {
            "answer": "2007",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/116"
        },
        {
            "answer": "2008",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/118"
        },
        {
            "answer": "2009",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/120"
        },
        {
            "answer": "2000",
            "caption": "الصوره هذي في اي عام ؟",
            "photo": "https://t.me/LANBOT2/122"
        },
        {
            "answer": "انشيلوتي",
            "caption": "شنو اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/124"
        },
        {
            "answer": "مورينيو",
            "caption": "شنو اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/126"
        },
        {
            "answer": "بيب غوارديولا",
            "caption": "شنو اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/128"
        },
        {
            "answer": "هيرفي رينارد",
            "caption": "شنو اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/130"
        },
        {
            "answer": "زيدان",
            "caption": "شنو اسم المدرب ؟",
            "photo": "https://t.me/LANBOT2/132"
        }
]
questions = [
    "شلون تعمل هالشي؟",
    "شلون تقضي وقتك بالفراغ؟",
    "شلون تتحكم بالضغط؟",
    "شلون تكون صبور؟",
    "شلون تحافظ على التركيز؟",
    "شلون تكون قوي نفسياً؟",
    "شلون تسيطر على الغضب؟",
    "شلون تدير وقتك بشكل فعال؟",
    "شلون تكون ناجح في حياتك المهنية؟",
    "شلون تطور مهاراتك الشخصية؟",
    "شلون تدير الضغوطات في العمل؟",
    "شلون تدير الامور المالية؟",
    "شلون تتعلم لغة جديدة؟",
    "شلون تكون مبدع في عملك؟",
    "شلون تطور علاقاتك الاجتماعية؟",
    "شلون تتغلب على التحديات؟",
    "شلون تنظم حياتك بشكل منظم؟",
    "شلون تحافظ على صحتك؟",
    "شلون تحمي نفسك من الإجهاد؟",
    "شلون تعتني بنفسك بشكل جيد؟",
    "شلون تكون متفائل في الحياة؟",
    "شلون تدير الوقت بين العمل والحياة الشخصية؟",
    "شلون تتعامل مع الشكوك والتوتر؟",
    "شلون تعطي قيمة لوقتك؟",
    "شلون تدير التوتر في العلاقات العائلية؟",
    "شلون تتعلم من الاخطاء؟",
    "شلون تدير الصعوبات في الحياة؟",
    "شلون تكون منظم في حياتك اليومية؟",
    "شلون تحسن من تركيزك وانتباهك؟",
    "شلون تطور مهاراتك الشخصية والاجتماعية؟",
    "شلون تدير العمل في فريق؟",
    "شلون تحسن من قدراتك التواصلية؟",
    "شلون تكون منظم في الدراسة؟",
    "شلون تكون فعال في استخدام التكنولوجيا؟",
    "شلون تحافظ على توازنك بين العمل والحياة الشخصية؟",
    "شلون تتعلم مهارات جديدة بسرعة؟",
    "شلون تكون ملهماً للآخرين؟",
    "شلون تدير الخلافات في العمل؟",
    "شلون تكون مؤثراً في العروض التقديمية؟",
    "شلون تحسن من قدراتك التفكير الإبداعي؟",
    "شلون تطور قدراتك القيادية؟",
    "شلون تكون متفائل في ظروف صعبة؟",
    "شلون تدير التحولات في الحياة؟",
    "شلون تتعلم من النجاحات والإخفاقات؟",
    "شلون تكون مستعداً للتغيير؟",
    "شلون تستمتع بالحياة؟",
    "شلون تكون إنساناً محبوباً ومحترماً؟",
    "شلون تتعلم من خبرات الآخرين؟",
    "شلون تطور مهاراتك في التعلم الذاتي؟",
    "شلون تحسن من قدراتك على اتخاذ القرارات؟",
    "شلون تكون مبادراً في العمل؟",
    "شلون تطور مهاراتك في حل المشكلات؟",
    "شلون تستفيد من النقد البناء؟",
    "شلون تطور ثقتك بالنفس؟",
    "شلون تتعامل مع التغييرات في العمل؟",
    "شلون تطور مهاراتك في التعاون والعمل الجماعي؟",
    "شلون تتعامل مع الضغوطات في الحياة؟",
    "شلونك؟",
    "شنو اسمك؟",
    "شنو جنسيتك؟",
    "شنو عمرك؟",
    "شنو لونك المفضل؟",
    "شنو طبخة تحبها اكثر؟",
    "شنو هوايتك المفضلة؟",
    "شنو مكان سفرة اللي تحلم تروحله؟",
    "شنو نوع السيارة اللي تفضلها؟",
    "شنو نوع الموسيقى اللي تحب تستمع لها؟",
    "شنو تحب تسوي في وقت الفراغ؟",
    "شنو اكلتك المفضلة في الفطور؟",
    "شنو اكلتك المفضلة في الغدا؟",
    "شنو اكلتك المفضلة في العشا؟",
    "شنو نوع الشاي اللي تحب تشربه؟",
    "شنو نوع القهوة اللي تحب تشربها؟",
    "شنو اكثر شيء مميز في ثقافة العراق؟",
    "شنو نوع الافلام اللي تحب تشوفها؟",
    "شنو البلدة العربية اللي تفضل تزورها؟",
    "شنو نوع الهدية اللي تحب تتلقاها؟",
    "شنو اهم شيء بالنسبة إليك في الصداقة؟",
    "شنو الشيء اللي تشوفه عند العراقيين بشكل خاص؟",
    "شنو الاكلة العراقية المفضلة عندك؟",
    "شنو نوع الرياضة اللي تحب تمارسها؟",
    "شنو مكان العراقي اللي تحب تزوره في العراق؟",
    "شنو اكثر شيء تحبه في الطبيعة؟",
    "شنو اللون اللي يحبه العراقيين كثير؟",
    "شنو الشيء اللي يستفزك بسرعة؟",
    "شنو الشيء اللي يخليك تفرح؟",
    "شنو الشيء اللي تحس إنه اكثر شيء يعبر عن الهوية العراقية؟",
    "شنو نوع الهاتف اللي تستخدمه؟",
    "شنو الشيء اللي تحس فيه إنه مفقود في المجتمع العراقي؟",
    "شنو اكثر مكان تحب تزوره في العراق؟",
    "شنو النصيحة اللي تحب تعطيها لشخص صغير؟",
    "شنو الشيء اللي يخليك تشعر بالراحة والهدوء؟",
    "شنو الشيء اللي تحب تسويه بالعطلة؟",
    "شنو الحيوان اللي تحبه اكثر؟",
    "شنو الشيء اللي تحب تهديه لشخص عزيز عليك؟",
    "شنو الشيء اللي تحس بإنجاز كبير إذا قمت به؟",
    "شنو اكثر موقع التواصل الاجتماعي اللي تستخدمه؟",
    "شنو الشيء اللي يحبه العراقيين في الاعياد والمناسبات؟",
    "شنو الشيء اللي تحب تشوفه في العراق مطور ومتطور؟",
    "شنو الشيء اللي تحب تشاركه مع الآخرين بشكل كبير؟",
    "شنو اكثر موسم تحبه في العراق؟",
    "شنو الشيء اللي تتمنى تغيره في العراق؟",
    "شنو الشيء اللي تحب تستثمر فيه وقتك وجهدك؟",
    "شنو الشيء اللي يميز العراق والعراقيين برايك؟",
    "شنو نوع الفن اللي تحب تستمتع به؟",
    "شنو الشيء اللي تحب تتعلمه في المستقبل؟",
    "شنو اكثر شيء تحبه في الشتاء؟",
    "شنو الشيء اللي يرفع معنوياتك بشكل سريع؟",
    "شنو الشيء اللي تحب تهديه لنفسك؟",
    "شنو الشيء اللي تتمنى تحققه في حياتك؟",
     "منو افضل صديق عندك؟",
    "منو شخصيتك المفضلة في الافلام؟",
    "منو الشخص اللي تحب تسافر معه؟",
    "منو الشخص اللي بتستشيره في قراراتك؟",
    "منو اكثر شخص تحب تشوفه كل يوم؟",
    "منو اكثر شخص غريب بتعرفه؟",
    "منو الشخص اللي تحب تحجي معه لساعات؟",
    "منو اكثر شخص قدوة بحياتك؟",
    "منو الشخص اللي تثق فيه بشكل كامل؟",
    "منو اكثر شخص ملهم في حياتك؟",
    "منو الشخص اللي تتمنى تشوفه اليوم؟",
    "منو الشخص اللي تحب تكون جارك؟",
    "منو الشخص اللي بتتحدث معه كل يوم؟",
    "منو الشخص اللي بتشتاقله كثير؟",
    "منو الشخص اللي بتعتمد عليه في الصعوبات؟",
    "منو الشخص اللي تحب تشاركه اسرارك؟",
    "منو الشخص اللي بتقدر قيمته في حياتك؟",
    "منو الشخص اللي تحب تطلب منه المشورة؟",
    "منو الشخص اللي تحب تكون معه في المشاكل؟",
    "منو الشخص اللي بتحسه اكثر شخص يفهمك؟",
    "منو الشخص اللي تحب تحتفل معه في الاعياد؟",
    "منو الشخص اللي تتوقعه اكثر شخص بيرحل عنك؟",
    "منو الشخص اللي تحب تشترك معه في الهوايات؟",
    "منو الشخص اللي تحب تشوفه بعد غياب طويل؟",
    "منو الشخص اللي تتمنى تقدمله هدية مميزة؟",
    "منو الشخص اللي تحب تذهب معه في رحلة استكشافية؟",
    "منو الشخص اللي تحب تحجي معه عن مشاكلك العاطفية؟",
    "منو الشخص اللي تتمنى تكون له نفس قدراتك ومهاراتك؟",
    "منو الشخص اللي تحب تقابله وتشتغل معه في المستقبل؟",
    "منو الشخص اللي تحب تحتفل معه بنجاحك وإنجازاتك؟",
    "منو الشخص اللي بتتذكره بكل سعادة عندما تراجع صورك القديمة؟",
    "منو الشخص اللي تحب تشاركه تجاربك ومغامراتك في الحياة؟",
    "منو الشخص اللي تحب تسمع نصائحه وتطبقها في حياتك؟",
    "منو الشخص اللي تحب تشوفه ضحكته بين الفينة والاخرى؟",
    "منو الشخص اللي تعتبره اكثر شخص يدعمك ويحفزك على تحقيق اهدافك؟",
    "منو الشخص اللي تحب تشوفه محقق نجاحاته ومستقبله المشرق؟",
    "منو الشخص اللي تحب تشكره على وجوده في حياتك ودعمه المستمر؟",
    "منو الشخص اللي تحب تقدمله هدية تذكارية لتخليك تذكره للابد؟",
    "منو الشخص اللي تحب تشكره على دعمه الكبير لك في مشوارك الدراسي؟",
    "منو الشخص اللي تتمنى تعرفه في المستقبل وتصير صداقتكم مميزة؟",
    "منو الشخص اللي تحب تشاركه لحظات الفرح والسعادة في حياتك؟",
    "منو الشخص اللي تعتبره اكثر شخص يستحق منك كل الحب والاحترام؟",
    "منو الشخص اللي تحب تشاركه اسرارك وتحجي له كل شيء بدون تردد؟",
    "منو الشخص اللي تتمنى تحضر معه حفلة موسيقية لفرقتك المفضلة؟",
    "منو الشخص اللي تحب تتنافس معه في لعبة او رياضة تحبها؟",
    "منو الشخص اللي تحب تشوفه مبتسماً ومتفائلاً في الحياة؟",
    "شوكت تفتح المحل؟",
    "شوكت بتروح على العمل؟",
    "شوكت تكون مستعد للمقابلة؟",
    "شوكت بتنوم بالليل؟",
    "شوكت بتصحى بالصبح؟",
    "شوكت بتسافر؟",
    "شوكت بتعود من العمل؟",
    "شوكت بتعمل رياضة؟",
    "شوكت بتذاكر للامتحان؟",
    "شوكت بتنظف البيت؟",
    "شوكت بتقرا الكتاب؟",
    "شوكت تكون فاضي للتسوق؟",
    "شوكت بتنطر الباص؟",
    "شوكت بتعود من السفر؟",
    "شوكت بتشتري الهدية؟",
    "شوكت بتتقابل مع صديقك؟",
    "شوكت بتحضر الحفلة؟",
    "شوكت بتتعشى؟",
    "شوكت بتتناول الفطور؟",
    "شوكت بتسافر في العطلة؟",
    "شوكت بترجع للمنزل؟",
    "شوكت تخلص المشروع؟",
    "شوكت بتتخرج من الجامعة؟",
    "شوكت بتبدا العمل؟",
    "شوكت بتفتح المحل؟",
    "شوكت تنتهي الدورة التدريبية؟",
    "شوكت بتتزوج؟",
    "شوكت بترتب الغرفة؟",
    "شوكت تتعلم الموسيقى؟",
    "شوكت بترتب الوثائق؟",
    "شوكت بتسجل في النادي الرياضي؟",
    "شوكت تستلم الطلبية؟",
    "شوكت بتشوف الطبيب؟",
    "شوكت بتتناول الغداء؟",
    "شوكت تكون مستعد للسفر؟",
    "شوكت بتكمل المشروع؟",
    "شوكت تخلص الواجب؟",
    "شوكت تحصل على النتيجة؟",
    "شوكت تتعلم اللغة الجديدة؟",
    "شوكت بتحضر المؤتمر؟",
    "شوكت بتنهي الكتاب؟",
    "شوكت بتفتح المطعم؟",
    "شوكت بتسافر في الإجازة؟",
    "شوكت بتبدا التدريب؟",
    "شوكت تخلص المشروع الفني؟",
    "شوكت تنتهي الجلسة؟",
    "شوكت تتعلم الطبخ؟",
    "شوكت تستلم الشهادة؟",
    "شوكت بتبدا الرحلة؟",
    "شوكت بتنهي الاعمال المنزلية؟",
    "شوكت تكون فاضي للقراءة؟",
    "شوكت تستلم السيارة الجديدة؟",
    "شوكت بتتناول العشاء؟",
    "وين رايح؟",
    "وين تسكن؟",
    "وين بتشتغل؟",
    "وين بتروح في ايام العطلة؟",
    "وين تحب تسافر في العطلات؟",
    "وين تحب تروح مع الاصدقاء؟",
    "وين تكون في الساعة الثامنة صباحاً؟",
    "وين تكون في الساعة العاشرة مساءً؟",
    "وين تحب تتناول الإفطار؟",
    "وين تحب تتسوق؟",
    "وين تحب تتناول العشاء؟",
    "وين تكون في الساعة الثانية ظهراً؟",
    "وين تحب تمضي امسياتك؟",
    "وين تحب تقضي ايام العطلة؟",
    "وين تحب تزور المعالم السياحية؟",
    "وين تحب تشتري الهدايا؟",
    "وين تحب تتمرن وتمارس الرياضة؟",
    "وين تحب تذهب للتسوق؟",
    "وين تحب تقضي وقتك مع العائلة؟",
    "وين تكون في الساعة الخامسة مساءً؟"
]
CHANNEL = 'theholyqouran'
suras = {
    "سورة الفاتحة": 1,
    "سورة البقرة": 2,
    "سورة آل عمران": 3,
    "سورة ال عمران": 3,
    "سورة النساء": 4,
    "سورة المائده": 5,
    "سورة المائدة": 5,
    "سورة الأنعام": 6,
    "سورة الانعام": 6,
    "سورة الأعراف": 7,
    "سورة الاعراف": 7,
    "سورة الأنفال": 8,
    "سورة الانفال": 8,
    "سورة التوبة": 9,
    "سورة يونس": 10,
    "سورة هود": 11,
    "سورة يوسف": 12,
    "سورة الرعد": 13,
    "سورة ابراهيم": 14,
    "سورة إبراهيم": 14,
    "سورة الحجر": 15,
    "سورة النحل": 16,
    "سورة الاسراء": 17,
    "سورة الإسراء": 17,
    "سورة الكهف": 18,
    "سورة مريم": 19,
    "سورة طه": 20,
    "سورة الانبياء": 21,
    "سورة الأنبياء": 21,
    "سورة الحج": 22,
    "سورة المؤمنون": 23,
    "سورة المومنون": 23,
    "سورة الفرقان": 24,
    "سورة النور": 25,
    "سورة الشعراء": 26,
    "سورة العنكبوت": 27,
    "سورة النمل": 28,
    "سورة القصص": 29,
    "سورة الروم": 30,
    "سورة لقمان": 31,
    "سورة السجدة": 32,
    "سورة الأحزاب": 33,
    "سورة الاحزاب": 33,
    "سورة سبأ": 34,
    "سورة سبا": 34,
    "سورة فاطر": 35,
    "سورة يس": 36,
    "سورة الصافات": 37,
    "سورة ص": 38,
    "سورة الزمر": 39,
    "سورة غافر": 40,
    "سورة فصلت": 41,
    "سورة الشورى": 42,
    "سورة الزخرف": 43,
    "سورة الدخان": 44,
    "سورة الجاثية": 45,
    "سورة الاحقاف": 46,
    "سورة الأحقاف": 46,
    "سورة الفتح": 47,
    "سورة محمد": 48,
    "سورة الحجرات": 49,
    "سورة الذاريات": 50,
    "سورة ق": 51,
    "سورة النجم": 52,
    "سورة الطور": 53,
    "سورة القمر": 54,
    "سورة الرحمن": 55,
    "سورة الواقعة": 56,
    "سورة الحديد": 57,
    "سورة المجادلة": 58,
    "سورة الحشر": 59,
    "سورة الممتحنة": 60,
    "سورة الصف": 61,
    "سورة الجمعة": 62,
    "سورة المنافقون": 63,
    "سورة التغابن": 64,
    "سورة الطلاق": 65,
    "سورة التحريم": 66,
    "سورة الملك": 67,
    "سورة القلم": 68,
    "سورة الحاقة": 69,
    "سورة المعارج": 70,
    "سورة نوح": 71,
    "سورة الجن": 72,
    "سورة المزمل": 73,
    "سورة المدثر": 74,
    "سورة القيامة": 75,
    "سورة الإنسان": 76,
    "سورة الانسان": 76,
    "سورة المرسلات": 77,
    "سورة النبا": 80,
    "سورة النبأ": 80,
    "سورة النازعات": 78,
    "سورة عبس": 79,
    "سورة التكوير": 81,
    "سورة الانفطار": 82,
    "سورة الإنفطار": 82,
    "سورة المطففين": 83,
    "سورة الانشقاق": 84,
    "سورة البروج": 85,
    "سورة الطارق": 86,
    "سورة الاعلى": 87,
    "سورة الأعلى": 87,
    "سورة الغاشية": 88,
    "سورة الفجر": 89,
    "سورة البلد": 90,
    "سورة الشمس": 91,
    "سورة الليل": 92,
    "سورة الضحى": 93,
    "سورة الشرح": 94,
    "سورة التين": 96,
    "سورة العلق": 95,
    "سورة القدر": 97,
    "سورة البينة": 98,
    "سورة الزلزلة": 99,
    "سورة العاديات": 100,
    "سورة القارعة": 101,
    "سورة التكاثر": 102,
    "سورة العصر": 103,
    "سورة الهمزة": 104,
    "سورة الفيل": 105,
    "سورة قريش": 106,
    "سورة الماعون": 107,
    "سورة الكوثر": 108,
    "سورة الكافرون": 109,
    "سورة النصر": 110,
    "سورة المسد": 111,
    "سورة الاخلاص": 112,
    "سورة الإخلاص": 112,
    "سورة الفلق": 113,
    "سورة الناس": 114,
}
x_ar = {
    '🇦🇫': 'افغانستان',
    '🇦🇱': 'البانيا',
    '🇩🇿': 'الجزائر',
    '🇦🇸': 'ساموا الامريكيا',
    '🇦🇩': 'اندورا',
    '🇦🇴': 'انغولا',
    '🇦🇮': 'انغويلا',
    '🇦🇶': 'القارة القطبية الجنوبية',
    '🇦🇬': 'انتيغوا وبربودا',
    '🇦🇷': 'الارجنتين',
    '🇦🇲': 'ارمينيا',
    '🇦🇼': 'اوربا',
    '🇦🇺': 'استراليا',
    '🇦🇹': 'النمسا',
    '🇦🇿': 'اذربيجان',
    '🇧🇸': 'جزر الباهاما',
    '🇧🇭': 'البحرين',
    '🇧🇩': 'بنغلاديش',
    '🇧🇧': 'باربادوس',
    '🇧🇾': 'بيلاروس',
    '🇧🇪': 'بلجيكا',
    '🇧🇿': 'بليز',
    '🇧🇯': 'بنين',
    '🇧🇲': 'برمودا',
    '🇧🇹': 'بوتان',
    '🇧🇴': 'بوليفيا',
    '🇧🇦': 'البوسنة والهرسك',
    '🇧🇼': 'بوتسوانا',
    '🇧🇷': 'البرازيل',
    '🇧🇳': 'بروناي',
    '🇧🇬': 'بلغاريا',
    '🇧🇫': 'بوركينا فاسو',
    '🇧🇮': 'بوروندي',
    '🇰🇭': 'كمبوديا',
    '🇨🇲': 'الكاميرون',
    '🇨🇦': 'كندا',
    '🇨🇻': 'الراس الاخضر',
    '🇰🇾': 'جزر كايمان',
    '🇨🇫': 'جمهورية افريقيا الوسطى',
    '🇹🇩': 'تشاد',
    '🇨🇱': 'تشيلي',
    '🇨🇳': 'الصين',
    '🇨🇴': 'كولومبيا',
    '🇰🇲': 'جزر القمر',
    '🇨🇬': 'الكونغو',
    '🇨🇩': 'جمهورية الكونغو الديمقراطية',
    '🇨🇷': 'كوستاريكا',
    '🇭🇷': 'كرواتيا',
    '🇨🇺': 'كوبا',
    '🇨🇾': 'قبرص',
    '🇨🇿': 'التشيك',
    '🇩🇰': 'الدنمارك',
    '🇩🇯': 'جيبوتي',
    '🇩🇴': 'جمهورية الدومينيكان',
    '🇪🇨': 'الاكوادور',
    '🇪🇬': 'مصر',
    '🇸🇻': 'السلفادور',
    '🇪🇷': 'اريتريا',
    '🇪🇪': 'استونيا',
    '🇪🇹': 'اثيوبيا',
    '🇫🇯': 'فيجي',
    '🇫🇮': 'فنلندا',
    '🇫🇷': 'فرنسا',
    '🇬🇦': 'الغابون',
    '🇬🇲': 'غامبيا',
    '🇩🇪': 'المانيا',
    '🇬🇭': 'غانا',
    '🇬🇷': 'اليونان',
    '🇬🇹': 'غواتيمالا',
    '🇬🇳': 'غينيا',
    '🇬🇼': 'غينيا بيساو',
    '🇭🇳': 'هندوراس',
    '🇭🇺': 'المجر',
    '🇮🇸': 'ايسلاندا',
    '🇮🇳': 'الهند',
    '🇮🇩': 'اندونوسيا',
    '🇮🇷': 'ايران',
    '🇮🇶': 'العراق',
    '🇮🇪': 'ايرلندا',
    '🇮🇱': 'اسرائيل',
    '🇮🇹': 'ايطاليا',
    '🇯🇲': 'جامايكا',
    '🇯🇵': 'اليابان',
    '🇯🇴': 'الاردن',
    '🇰🇿': 'كازاخستان',
    '🇰🇪': 'كينيا',
    '🇰🇼': 'الكويت',
    '🇰🇬': 'قرغيزستان',
    '🇱🇦': 'لاوس',
    '🇱🇻': 'لاتفيا',
    '🇱🇧': 'لبنان',
    '🇱🇸': 'ليسوتو',
    '🇱🇷': 'ليبيريا',
    '🇱🇾': 'ليبيا',
    '🇱🇹': 'ليتوانيا',
    '🇱🇺': 'لوكسمبورغ',
    '🇲🇰': 'مقدونيا الشمالية',
    '🇲🇬': 'مدغشقر',
    '🇲🇼': 'ملاوي',
    '🇲🇾': 'ماليزيا',
    '🇲🇻': 'المالديف',
    '🇲🇱': 'مالي',
    '🇲🇹': 'مالطا',
    '🇲🇷': 'موريتانيا',
    '🇲🇺': 'موريشيوس',
    '🇲🇽': 'المكسيك',
    '🇫🇲': 'ميكرونيزيا',
    '🇲🇩': 'مولدوفا',
    '🇲🇨': 'موناكو',
    '🇲🇳': 'منغوليا',
    '🇲🇪': 'الجبل الاسود',
    '🇲🇦': 'المغرب',
    '🇲🇿': 'موزمبيق',
    '🇳🇦': 'ناميبيا',
    '🇳🇵': 'نيبال',
    '🇳🇱': 'هولندا',
    '🇳🇿': 'نيوزيلندا',
    '🇳🇮': 'نيكاراغوا',
    '🇳🇪': 'النيجر',
    '🇳🇬': 'نيجيريا',
    '🇰🇵': 'كوريا الشمالية',
    '🇳🇴': 'النرويج',
    '🇴🇲': 'عمان',
    '🇵🇰': 'باكستان',
    '🇵🇦': 'بنما',
    '🇵🇬': 'بابوا غينيا الجديدة',
    '🇵🇾': 'باراغواي',
    '🇵🇪': 'بيرو',
    '🇵🇭': 'الفلبين',
    '🇵🇱': 'بولندا',
    '🇵🇹': 'البرتغال',
    '🇶🇦': 'قطر',
    '🇷🇴': 'رومانيا',
    '🇷🇺': 'روسيا',
    '🇷🇼': 'رواندا',
    '🇸🇦': 'السعودية',
    '🇸🇳': 'السنغال',
    '🇷🇸': 'صربيا',
    '🇸🇬': 'سنغافورة',
    '🇸🇰': 'سلوفاكيا',
    '🇸🇮': 'سلوفينيا',
    '🇿🇦': 'جنوب افريقيا',
    '🇰🇷': 'كوريا الجنوبية',
    '🇪🇸': 'اسبانيا',
    '🇱🇰': 'سريلانكا',
    '🇸🇩': 'السودان',
    '🇸🇷': 'سورينام',
    '🇸🇪': 'السويد',
    '🇨🇭': 'سويسرا',
    '🇸🇾': 'سوريا',
    '🇹🇯': 'طاجيكستان',
    '🇹🇿': 'تنزانيا',
    '🇹🇭': 'تايلاند',
    '🇹🇱': 'تيمور الشرقية',
    '🇹🇬': 'توغو',
    '🇹🇴': 'تونغا',
    '🇹🇳': 'تونس',
    '🇹🇷': 'تركيا',
    '🇹🇲': 'تركمانستان',
    '🇺🇬': 'اوغندا',
    '🇺🇦': 'اوكرانيا',
    '🇦🇪': 'الامارات',
    '🇬🇧': 'المملكة المتحدة',
    '🇺🇸': 'الولايات المتحدة',
    '🇺🇾': 'اوروغواي',
    '🇺🇿': 'اوزباكستان',
    '🇻🇳': 'فيتنام',
    '🇾🇪': 'اليمن',
    '🇿🇲': 'زامبيا',
    '🇿🇼': 'زيمبابوي',
}
