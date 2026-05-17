from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import ChatParticipantCreator
from telethon.errors import UserNotParticipantError
import pytz, os, json, asyncio, time, inspect
from telethon.tl.types import ReactionEmoji
import google.generativeai as genai, re
from telethon import types, Button
from types import SimpleNamespace
from ABH import ABH, r, events
from typing import Dict, Any
from functools import wraps
from telethon import types
from ABH import *
async def execute_alias_engine(event):
    chat_id = event.chat_id
    text = event.raw_text
    parts = text.split(maxsplit=1)
    if not parts:
        return
    incoming_shortcut = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""    
    real_cmd = r.hget(f"cmd:{chat_id}", incoming_shortcut)    
    if real_cmd:
        event.raw_text = f"{real_cmd} {args}"        
        try:
            event._parse_msg()
            await ABH._dispatch_event(event)
        except:
            pass
ALIASES_CACHE = {} 
LAST_UPDATE_TIMES = {}
CACHE_TTL = 100
async def update_local_cache(chat_id):
    global ALIASES_CACHE, LAST_UPDATE_TIMES
    try:
        keys = r.keys(f"cmd:{chat_id}:*")
        new_data = {k.split(':')[-1]: {s for s in r.smembers(k)} for k in keys}
        ALIASES_CACHE[chat_id] = new_data
        LAST_UPDATE_TIMES[chat_id] = time.time()
    except: pass
def anymous_cmd(main_pattern, **kwargs):
    def decorator(f):
        @ABH.on(events.NewMessage(**kwargs))
        async def wrapper(event):
            if not event.raw_text or not event.is_group:
                return
            chat_id = event.chat_id
            now = time.time()            
            last_upd = LAST_UPDATE_TIMES.get(chat_id, 0)
            if now - last_upd > CACHE_TTL:
                await update_local_cache(chat_id)
            text = event.raw_text.strip() 
            match = re.fullmatch(main_pattern, text)
            if match:
                event.pattern_match = match
                return await f(event)
            first_word_raw = text.split()[0]
            first_word = first_word_raw            
            for prefix in ['/', '!', '.', '']:
                if prefix and first_word.startswith(prefix):
                    first_word = first_word[len(prefix):]
                    break            
            clean_cmd_match = re.search(r'[آ-يa-zA-Z0-9\s]+', main_pattern)
            group_name = clean_cmd_match.group(0).strip() if clean_cmd_match else ""
            chat_cache = ALIASES_CACHE.get(chat_id, {})            
            if group_name in chat_cache and first_word in chat_cache[group_name]:
                fake_text = re.sub(re.escape(first_word_raw), group_name, text, count=1)
                new_match = re.fullmatch(main_pattern, fake_text)
                if new_match:
                    event.pattern_match = new_match
                    return await f(event)
        return wrapper
    return decorator
def timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()        
        result = await func(*args, **kwargs)        
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
    """جلب بيانات المستخدم بالكامل من Redis"""
    data = r.get(f"user:{user_id}")
    return json.loads(data) if data else None
def save_user(user_id, data):
    """حفظ بيانات المستخدم (JSON)"""
    r.set(f"user:{user_id}", json.dumps(data, ensure_ascii=False))
async def get_input_media(media_data):
    """تحويل قاموس الميديا المخزن إلى كائن InputMedia جاهز للإرسال"""
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
async def get_profile_photo(id):
    photos = []
    try:
        user = await ABH.get_entity(id)
        photos = await ABH.get_profile_photos(user, limit=1)
        if photos:
            return photos[0]
        else:
            return None
    except:
            return None
async def bot():
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
    full_users = await ABH.get_entity(users)    
    for user in full_users:
        profilename = profile(user.id)        
        if profilename:
            name = profilename.first_name
        elif getattr(user, 'first_name', None):
            name = user.first_name
        else:
            name = "حساب محذوف"            
        mention.append(f"[{name}](tg://user?id={user.id}) {text} `{user.id}`")            
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
actions = [
    'يوتيوب', 'تقييد', 'ردود', 'تنظيف', 'تحذير', 
    'منع', 'العاب', 'همسة', 'ترقية', 'رفع', 
    'ايدي', 'توب', 'تعديل', 'اوامر العامة', 'ميم'
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
async def raise_commands(event):
    if not event.is_group:return
    if event.text == 'اوامر الفتح والتعطيل':
        return await event.reply(lockANDunlock)
    category = event.pattern_match.group(1)
    cmds_list = allcommands.get(category, [])
    commands = f"**{event.text}**\n\n" + "\n".join(f"{i} - `{cmd}` " for i, cmd in enumerate(cmds_list, start=1))
    await event.reply(commands)
unicode = "\u200f"
def lock(e, type):
    lock_key = f"lock:{e.chat_id}:{type}"
    return r.get(lock_key) == "True"
@ABH.on(events.NewMessage(pattern='^نقل ملكية البوت$', from_users=[1910015590]))
async def tansferbotowner(e):
    global wfffp
    r = await e.get_reply_message()
    if not r:
        return await e.reply('عذرا بس ل خطوره الامر لازم تشغله بالرد')
    wfffp = r.sender_id
    m = await ment(wfffp)
    b = await bot()
    await e.reply(f'تم نقل ملكية البوت {b['full_name']} الى المستخدم {m}')
    try:
        await ABH.send_message(wfffp, 'مرحبا عزيزي {} انت حاليا المطور الاساسي الجديد واني راح اساعدك , انت حاليا المالك مالتي'.format(m))
    except:
        pass
    # await asyncio.sleep(60)
    # await ABH.send_message(wfffp, 'هههههههه ضحكنه عليك يالغالي , رجعت ابن هاش مطور و نزلتك')
    # wfffp = 1910015590
    # await e.respond(file='https://t.me/recoursec/30', message='تم ارجاع الملكية الى المطور الاصلي ابن هاشم السبب \n لان واحد عراق', reply_to=e.id)
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
    'المالك': 2, 
    'المطور ثانوي': 3,
    'المساعد': 4, 
    'المعاون': 5,
}
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
    'اوامر العامة': 'المطور الثانوي',
    'تعديل': 'المطور الثانوي',
    'ترقية': 'المطور الثانوي',
    'ميم': 'المعاون'
}
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
async def to(e, args=1, text=None):
    'target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)'
    try:
        reply = await e.get_reply_message()
        if reply:
            return reply
        args = text if text else e.pattern_match.group(int(args))
        target = args.strip() if args else None
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
CACHE_TIME = 120 
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
WARN_FILE = "warns.json"
def load_warns():
    if os.path.exists(WARN_FILE):
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
def save_warns(warns_data):
    with open(WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(warns_data, f, ensure_ascii=False, indent=2)
def add_warning(user_id: int, chat_id: int) -> int:
    warns = load_warns()
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)
    if chat_id_str not in warns:
        warns[chat_id_str] = {}
    if user_id_str not in warns[chat_id_str]:
        warns[chat_id_str][user_id_str] = 0
    warns[chat_id_str][user_id_str] += 1
    current_warns = warns[chat_id_str][user_id_str]
    if current_warns >= 3:
        warns[chat_id_str][user_id_str] = 0
    save_warns(warns)
    return current_warns
def del_warning(user_id: int, chat_id: int) -> int:
    warns = load_warns()
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)
    if chat_id_str in warns and user_id_str in warns[chat_id_str]:
        if warns[chat_id_str][user_id_str] > 0:
            warns[chat_id_str][user_id_str] -= 1
            save_warns(warns)
            return warns[chat_id_str][user_id_str]
    return 0
def zerowarn(user_id: int, chat_id: int) -> int:
    warns = load_warns()
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)
    if chat_id_str in warns and user_id_str in warns[chat_id_str]:
        warns[chat_id_str][user_id_str] = 0
        save_warns(warns)
        return 0
    return 0
def count_warnings(user_id: int, chat_id: int) -> int:
    warns = load_warns()
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)
    if chat_id_str in warns and user_id_str in warns[chat_id_str]:
        return warns[chat_id_str][user_id_str]
    return 0
async def send(e, m, chat=None):
    c = chat if chat else e.chat_id
    l = LC(str(c))
    if not l:
        return
    await ABH.send_message(l, m)
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
async def res(المصدر=None, stop=False, t=20*60):
    if المصدر is None:
        all_keys = r.keys('*')
        return {key: r.hgetall(key) for key in all_keys}
    if isinstance(المصدر, str) and ":" in المصدر:
        parts = المصدر.split(":")
        chat_id, user_id = str(parts[0]), str(parts[1])
    else:
        chat_id, user_id = str(المصدر.chat_id), str(المصدر.sender_id)
    end_time = int(time.time()) + (t or 20)    
    r.hset(chat_id, user_id, end_time)
    if stop:
        return r.hgetall(chat_id)
    now = int(time.time())
    rights = ChatBannedRights(
        until_date=now + (t or 20),
        send_messages=True
    )
    await ABH(EditBannedRequest(channel=int(chat_id), participant=int(user_id), banned_rights=rights))
    return r.hgetall(chat_id)
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
    usernames = []    
    if getattr(user_object, "usernames", None):
        for u in user_object.usernames:
            if getattr(u, "username", None):
                usernames.append(u.username)    
    if getattr(user_object, "username", None):
        usernames.insert(0, user_object.username)    
    usernames = list(dict.fromkeys(usernames))
    return usernames
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
async def try_forward(event, r=None, chat=None, id=None):
    gidvar = LC(event.chat_id)
    if not gidvar:
        return False
    try:
        if id:
            msg = id
        elif r:
            msg = r.id
        else:
            msg = event.id
        from_peer = chat if chat else event.chat_id
        await ABH.forward_messages(
            entity=int(gidvar),
            messages=msg,
            from_peer=from_peer
        )
    except Exception as e:
        # await hint(e)
        return False
    return True
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
async def get_owner(event, client=ABH):
    try:
        chat = await event.get_chat()
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            result = await client(GetParticipantsRequest(
                channel=await event.get_input_chat(),
                filter=ChannelParticipantsAdmins(),
                offset=0,
                limit=100,
                hash=0
            ))
            for participant in result.participants:
                if isinstance(participant, ChannelParticipantCreator):
                    return await client.get_entity(participant.user_id)
        else:
            full = await client(GetFullChatRequest(chat.id))
            if full.full_chat.participants:
                for participant in full.full_chat.participants.participants:
                    if isinstance(participant, ChatParticipantCreator):
                        return await client.get_entity(participant.user_id)
    except Exception as e:
        await hint(f"Error in get_owner: {e}")
        return None
    return None
timezone = pytz.timezone('Asia/Baghdad')
GEMINI = "AIzaSyA5pzOpKVcMGm6Aek82KoB3Pk94dYg3LX4"
genai.configure(api_key=GEMINI)
model = genai.GenerativeModel("gemini-1.5-flash")
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
async def ment(entity):
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
لطميات = {
    "من هو العباس": {
        "message_id": 50
    },
    "هلا ب اربعينه": {
        "message_id": 51
    },
    "جداه": {
        "message_id": 52
    },
    "عدلين ميتين يمك": {
        "message_id": 53
    },
    "حروبك ياعلي": {
        "message_id": 54
    },
    "راية العباس": {
        "message_id": 55
    },
    "غضب الله": {
        "message_id": 56
    },
    "اعصار العباس": {
        "message_id": 57
    },
    "معكم معكم": {
        "message_id": 58
    },
    "خيرة الله من الخلق ابي": {
        "message_id": 59
    },
    "قرة عين": {
        "message_id": 60
    },
    "ليالي الجروح": {
        "message_id": 61
    },
    "موعود الك": {
        "message_id": 62
    },
    "الى الوداع سيدي": {
        "message_id": 63
    },
    "نصراً من الله وفتح قريبll ملا مجتبى الكعبي ll موكب عشق علي -البص": {
        "message_id": 64
    },
    "يبن عم المصطفى وياساعده": {
        "message_id": 66
    },
    "عباس بونينك": {
        "message_id": 67
    },
    "طلعت زلمنة": {
        "message_id": 68
    },
    "رحلة": {
        "message_id": 69
    },
    "ابد والله لن ننسى حسينا": {
        "message_id": 70
    },
    "ها يمهدي": {
        "message_id": 73
    },
    "ها عليهم": {
        "message_id": 74
    },
    "ابد والله يا زهراء ما ننسى حسيناه": {
        "message_id": 75
    },
    "شد الثامه": {
        "message_id": 76
    },
    "لزمة علينه المشرعه": {
        "message_id": 78
    },
    "فروا الى الحسين": {
        "message_id": 83
    },
    "صوت احساس": {
        "message_id": 84
    },
    "الساقي": {
        "message_id": 85
    },
    "يا نجمه": {
        "message_id": 86
    },
    "يالابس ثياب العرس وين العرس": {
        "message_id": 87
    },
    "ذوله الولد": {
        "message_id": 88
    },
    "شيخ النشامه": {
        "message_id": 89
    },
    "ام وهب": {
        "message_id": 90
    },
    "حسينا": {
        "message_id": 91
    },
    "راياتنا": {
        "message_id": 92
    },
    "ما بيننا ايات": {
        "message_id": 95
    },
    "ملكك وانت ديني": {
        "message_id": 96
    },
    "عيد الغدير بنكهة اهوازية": {
        "message_id": 97
    },
    "مشوار الحب": {
        "message_id": 99
    },
    "اطوي الارض": {
        "message_id": 100
    },
    "دنيا": {
        "message_id": 101
    },
    "يالراهب برسمه": {
        "message_id": 102
    },
    "طلعت يحسين المشاية": {
        "message_id": 103
    },
    "شايل اصرار": {
        "message_id": 104
    },
    "قمر الال هلا": {
        "message_id": 105
    },
    "صورة علي": {
        "message_id": 106
    },
    "ام الوجود": {
        "message_id": 107
    },
    "عصابة امي الماطاحت": {
        "message_id": 108
    },
    "خطة حرب": {
        "message_id": 109
    },
    "كلبي ضامي": {
        "message_id": 112
    },
    "سامحيني": {
        "message_id": 113
    },
    "شيخ الخدام": {
        "message_id": 116
    },
    "زينب لفت": {
        "message_id": 117
    },
    "نزله  الرادود احمد الفتلاوي": {
        "message_id": 118
    },
    "حديث الموت": {
        "message_id": 119
    },
    "جبنالك ماي ويانه": {
        "message_id": 120
    },
    "اول خليفة": {
        "message_id": 122
    },
    "يا ساقي الماي": {
        "message_id": 123
    },
    "شكراً جزيلاً عباس": {
        "message_id": 124
    },
    "بندرية الرادود خضر عباس": {
        "message_id": 125
    },
    "هوسات العباس": {
        "message_id": 126
    },
    "هوسات الموت": {
        "message_id": 127
    },
    "طبت عراضه كوم طب عليهم": {
        "message_id": 128
    },
    "مجانينه": {
        "message_id": 129
    },
    "مات الورد": {
        "message_id": 130
    },
    "ياكلبي كافي ولم العتاب": {
        "message_id": 132
    },
    "حبست دموع عيني": {
        "message_id": 133
    },
    "سد عينك": {
        "message_id": 134
    },
    "شد عليهم": {
        "message_id": 135
    },
    "هذا كافل زينب": {
        "message_id": 137
    },
    "عباس لو علي": {
        "message_id": 138
    },
    "ناحر الحومه": {
        "message_id": 139
    },
    "خجلانه هواي": {
        "message_id": 140
    },
    "قارورة": {
        "message_id": 141
    },
    "النوايب صوبني": {
        "message_id": 143
    },
    "وليدي القمر": {
        "message_id": 144
    },
    "بجيتك": {
        "message_id": 145
    },
    "مرت سنة ونص": {
        "message_id": 146
    },
    "اين استقرت يا ابو صالح": {
        "message_id": 147
    },
    "العلم عالكاع يا حيدر": {
        "message_id": 149
    },
    "اشهدوله": {
        "message_id": 151
    },
    "ذوله خوتهم صدك": {
        "message_id": 153
    },
    "للمشرعه تعنيت": {
        "message_id": 154
    },
    "الخدم بحماك": {
        "message_id": 155
    },
    "هله يا هيبة": {
        "message_id": 156
    },
    "نصر الله": {
        "message_id": 157
    },
    "كلشي مات": {
        "message_id": 158
    },
    "لاترحلي": {
        "message_id": 160
    },
    "ان وعد الله حق": {
        "message_id": 161
    },
    "يا زينب": {
        "message_id": 163
    },
    "هاي الزلم": {
        "message_id": 164
    },
    "تسبيحة عشاق": {
        "message_id": 165
    },
    "سلام الله": {
        "message_id": 166
    },
    "يا باب الحوائج حاجتي يمك": {
        "message_id": 167
    },
    "سيد الاحساس": {
        "message_id": 168
    },
    "الفصول الاربعة": {
        "message_id": 169
    },
    "طبع الشمع": {
        "message_id": 170
    },
    "تدري لو متدري": {
        "message_id": 171
    },
    "سامحني": {
        "message_id": 172
    },
    "قلب مجروح": {
        "message_id": 173
    },
    "ياحي الله الاكبر": {
        "message_id": 174
    },
    "قاللها صار": {
        "message_id": 176
    },
    "نتيجة غيبتك": {
        "message_id": 177
    },
    "انا من انا": {
        "message_id": 178
    },
    "ام البنين تنادي": {
        "message_id": 179
    },
    "نزلة نجفية ": {
        "message_id": 180
    },
    "زينب ردت من الشام": {
        "message_id": 205
    },
    "ملك الموت": {
        "message_id": 184
    },
    "عينك": {
        "message_id": 185
    },
    "لا فتى الا علي": {
        "message_id": 186
    },
    "رحل كل غالي": {
        "message_id": 188
    },
    "ندمان وراجعلك": {
        "message_id": 189
    },
    "منين اجيب الماي": {
        "message_id": 190
    },
    "انا الهلال": {
        "message_id": 191
    },
    "حيدر من وصلها": {
        "message_id": 192
    },
    "لا تتاخر عليه": {
        "message_id": 193
    },
    "يالمهدي": {
        "message_id": 195
    },
    "تذكرة عشق": {
        "message_id": 196
    },
    "الخير كله بخدمة حسين": {
        "message_id": 197
    },
    "طلع شباب من الخيم": {
        "message_id": 198
    },
    "اضحاب الحسين": {
        "message_id": 199
    },
    "يا طود الصبر": {
        "message_id": 200
    },
    "ياحيدر بباب الدار": {
        "message_id": 201
    },
    "اللهم عجل": {
        "message_id": 202
    },
    "ليلة وداع": {
        "message_id": 203
    },
    "عاشق وحسيني  ": {
        "message_id": 204
    },
    "شال الطف": {
        "message_id": 206
    },
    "مولاتي يا مولاتي": {
        "message_id": 207
    },
    "يا حادي الضعن ريض": {
        "message_id": 208
    },
    "مظلوم حسين جانم": {
        "message_id": 209
    },
    "هلا بك": {
        "message_id": 210
    },
    "علي حيدر يكرار": {
        "message_id": 211
    },
    "جف اليصافح": {
        "message_id": 213
    },
    "كل شي عباس": {
        "message_id": 214
    },
    "سامع اذ حب الكلب": {
        "message_id": 215
    },
    "الم سبي حرم": {
        "message_id": 216
    },
    "انا بنت الهتف جبريل": {
        "message_id": 217
    },
    "مات الولد مات": {
        "message_id": 218
    },
    "ضي منحرك": {
        "message_id": 219
    },
    "ها هو القاسم": {
        "message_id": 220
    },
    "بين المهدي والعباس": {
        "message_id": 221
    },
    "كولو علي": {
        "message_id": 222
    },
    "كل مايجي اليلvideo 2023": {
        "message_id": 224
    },
    "ليث المعركة": {
        "message_id": 225
    },
    "الماتم ثقافتنا": {
        "message_id": 226
    },
    "ياعلي مدد": {
        "message_id": 227
    },
    "نسل حيدرم": {
        "message_id": 228
    },
    "يا فاطمة يم الحسن": {
        "message_id": 229
    },
    "يا بوفاضل": {
        "message_id": 231
    },
    "براءة العشق": {
        "message_id": 232
    },
    "يخيمات": {
        "message_id": 233
    },
    "مصحفنه خط احمر": {
        "message_id": 234
    },
    "زينب وين": {
        "message_id": 235
    },
    "الكوثرية": {
        "message_id": 236
    },
    "نمشي مع الحجة": {
        "message_id": 238
    },
    "اجه الموت": {
        "message_id": 239
    },
    "رجعت ادين الطغيان": {
        "message_id": 240
    },
    "تصد للدرب عيني": {
        "message_id": 241
    },
    "ظلم كسر ضلع": {
        "message_id": 242
    },
    "سلطان الرفض": {
        "message_id": 243
    },
    "قيامه كربله": {
        "message_id": 244
    },
    "زينب نادت السجاد )": {
        "message_id": 246
    },
    "يسلطان المشاعر": {
        "message_id": 248
    },
    "شوط كربلائي": {
        "message_id": 249
    },
    "نحن لا نهزم": {
        "message_id": 250
    },
    "الله في الساحة": {
        "message_id": 251
    },
    "المد الشيعي": {
        "message_id": 252
    },
    " هيبة هاشم": {
        "message_id": 253
    },
    "قتال العرب": {
        "message_id": 255
    },
    "راعي الصيت": {
        "message_id": 265
    },
    "سمع الله لمن قال علي": {
        "message_id": 257
    },
    "انا ما املك وجودي": {
        "message_id": 258
    },
    "احنه خواله": {
        "message_id": 259
    },
    "عرس بارض الطفوف": {
        "message_id": 260
    },
    "سالفتي نحیب": {
        "message_id": 261
    },
    "مناجاة الحسين": {
        "message_id": 262
    },
    "هذا ابن فاطمة": {
        "message_id": 263
    },
    "في درب فاطمة": {
        "message_id": 264
    },
    "علي يامن قلعت الباب": {
        "message_id": 266
    },
    "يمه اطمنج عليه": {
        "message_id": 267
    },
    "وسط كلبي شحلاتك": {
        "message_id": 268
    },
    "مسلم يا ربات حسين ": {
        "message_id": 269
    },
    "تربات البدو": {
        "message_id": 270
    },
    "گوم يابو الجود": {
        "message_id": 271
    },
    "سلام يا مهدي": {
        "message_id": 272
    },
    "سلام يا مهدي": {
        "message_id": 274
    },
    "اجمل ساقي": {
        "message_id": 276
    },
    "صولة العباس": {
        "message_id": 277
    },
    "حي الله عباس": {
        "message_id": 278
    },
    "ربت زلم": {
        "message_id": 279
    },
    "ريت السافر يعود": {
        "message_id": 280
    },
    "يالمدلل يعبد الله": {
        "message_id": 281
    },
    "يا ام البنين": {
        "message_id": 282
    },
    "لحسين انتمائي": {
        "message_id": 283
    },
    "عقلي بجنون": {
        "message_id": 284
    },
    "يا با الفضل": {
        "message_id": 285
    },
    "بالله يا نهر": {
        "message_id": 286
    },
    "يا نبضا لاحساسي": {
        "message_id": 287
    },
    "الموت ارتبك": {
        "message_id": 288
    },
    "عد لي حبيبي": {
        "message_id": 289
    },
    "ائمتي وسادتي": {
        "message_id": 290
    },
    "حب بلا خصام": {
        "message_id": 291
    },
    "قمر كربلاء": {
        "message_id": 292
    },
    "ناذر سنيني": {
        "message_id": 293
    },
    "مثل طبع النسر طبعي": {
        "message_id": 294
    },
    "سلام عن بعد": {
        "message_id": 295
    },
    "حصن خيبر": {
        "message_id": 296
    },
    "امنياتي": {
        "message_id": 297
    },
    "فرحة السادة": {
        "message_id": 298
    },
    "كون يامرنا علي السيستاني": {
        "message_id": 299
    },
    "نزلة نجفية": {
        "message_id": 300
    },
    "حيرة حسين": {
        "message_id": 379
    },
    "اكتب عذابي": {
        "message_id": 305
    },
    "حراس العقيدة": {
        "message_id": 306
    },
    "كليم الحسين": {
        "message_id": 307
    },
    "طفح الدمع وقال": {
        "message_id": 308
    },
    "بروحي": {
        "message_id": 309
    },
    "يكرهوني واحبك": {
        "message_id": 310
    },
    "نوح و دمع": {
        "message_id": 311
    },
    "تركنا الخلق طرا": {
        "message_id": 312
    },
    "امير الجمال": {
        "message_id": 313
    },
    "رايح الغالي": {
        "message_id": 430
    },
    "ما ذنب طفلي": {
        "message_id": 315
    },
    "الوداع": {
        "message_id": 316
    },
    "ادعي يا زينب": {
        "message_id": 317
    },
    "ما ندري": {
        "message_id": 318
    },
    "والله افنيها": {
        "message_id": 319
    },
    "حي على العزاء": {
        "message_id": 320
    },
    "تجارة لن تبور": {
        "message_id": 321
    },
    "ما اشوف بعيني": {
        "message_id": 322
    },
    "جل جلاله": {
        "message_id": 323
    },
    "المشكاه السبعه": {
        "message_id": 324
    },
    "خطب العباس": {
        "message_id": 325
    },
    "الغيرة الهاشمية": {
        "message_id": 326
    },
    "عندي فتيان اربعة": {
        "message_id": 327
    },
    "طايح بين خياله": {
        "message_id": 328
    },
    "واويلاه يم الخدر": {
        "message_id": 329
    },
    "اقطع الكلام": {
        "message_id": 330
    },
    "برز القمر": {
        "message_id": 331
    },
    "هلا بحسين الثاني": {
        "message_id": 332
    },
    "وصية الاب": {
        "message_id": 334
    },
    "ديوانك حلم كل عاشك": {
        "message_id": 335
    },
    "هالله هالله حسين وينه": {
        "message_id": 336
    },
    "مسا الخير": {
        "message_id": 337
    },
    "يريح الهاب": {
        "message_id": 338
    },
    "لو حي النبي": {
        "message_id": 339
    },
    "لا تسافر روحي عندك": {
        "message_id": 340
    },
    "يسجلني": {
        "message_id": 341
    },
    "خلي عيونج بعيني": {
        "message_id": 342
    },
    "عتاب الموت": {
        "message_id": 343
    },
    "للعباس اجت زينب": {
        "message_id": 344
    },
    "عطر يوسف": {
        "message_id": 345
    },
    "امك فاطمة يحسين": {
        "message_id": 346
    },
    "اجانه الصبح": {
        "message_id": 347
    },
    "عين الله ترعاكم": {
        "message_id": 348
    },
    "سبحانه سواها": {
        "message_id": 349
    },
    "حسين قتيل": {
        "message_id": 350
    },
    "جائنا الظلام": {
        "message_id": 351
    },
    "يا محلى الوداع": {
        "message_id": 375
    },
    "ان جان هاذي كربلاء وين شيال العلم": {
        "message_id": 353
    },
    "اعظم عريسين": {
        "message_id": 354
    },
    "طبعي كربلائي": {
        "message_id": 355
    },
    "عاشور هل هلاله": {
        "message_id": 356
    },
    "يا ال هاشم": {
        "message_id": 357
    },
    "ملكني": {
        "message_id": 358
    },
    "شيخ الانصار": {
        "message_id": 359
    },
    "اعصار": {
        "message_id": 360
    },
    "وجه الصباح": {
        "message_id": 361
    },
    "الخيال الشيعي": {
        "message_id": 362
    },
    "الوعد الصادق": {
        "message_id": 363
    },
    "عهد النجباء": {
        "message_id": 364
    },
    "دهد يا عون": {
        "message_id": 366
    },
    "الهيبة اوبريت": {
        "message_id": 367
    },
    "فرحة حيدرية": {
        "message_id": 368
    },
    "فرحة غديرك": {
        "message_id": 369
    },
    "امام النحل": {
        "message_id": 370
    },
    "من المتمسكين": {
        "message_id": 371
    },
    "عطلتنه رسمية": {
        "message_id": 372
    },
    "اخيتكم في الله": {
        "message_id": 373
    },
    "كلما اسهر الليل": {
        "message_id": 374
    },
    "واقع لو حلم": {
        "message_id": 376
    },
    "اهز مهدك": {
        "message_id": 377
    },
    "قيامة العباس": {
        "message_id": 380
    },
    "محرم الذهب": {
        "message_id": 381
    },
    "علكو الرايات": {
        "message_id": 383
    },
    "زلم النيبه": {
        "message_id": 384
    },
    "ويلي يالاكبر حاجيني": {
        "message_id": 385
    },
    "حلو بيارغهم": {
        "message_id": 386
    },
    "انا دامي": {
        "message_id": 388
    },
    "اذان العشق": {
        "message_id": 389
    },
    "يا فاطمة قومي الى الطفوف": {
        "message_id": 392
    },
    "سيوف اهلك مالاكوها": {
        "message_id": 393
    },
    "هل يوم نعزي فاطمه": {
        "message_id": 394
    },
    "حطيتلك عله بدليلي": {
        "message_id": 395
    },
    "يالماشي لبعيد": {
        "message_id": 396
    },
    "انا ام الرواي": {
        "message_id": 397
    },
    "مقتل الحسين": {
        "message_id": 398
    },
    "اهات الحسين": {
        "message_id": 399
    },
    "مسلم وسبع الكنطرة": {
        "message_id": 400
    },
    "ابطال هجت": {
        "message_id": 401
    },
    "اوتار التكبير": {
        "message_id": 402
    },
    "اويلي حسين طايح": {
        "message_id": 403
    },
    "قصة حزن": {
        "message_id": 404
    },
    "ما تذل شيعة علي": {
        "message_id": 405
    },
    "كلبك مكاني": {
        "message_id": 406
    },
    "بسملة الطف": {
        "message_id": 407
    },
    "جمال الله": {
        "message_id": 408
    },
    "طال انتظاري": {
        "message_id": 409
    },
    "اجمل علاقة": {
        "message_id": 410
    },
    "سمعي يمي فاطمة": {
        "message_id": 411
    },
    "مسلم الكوفه": {
        "message_id": 422
    },
    "ها يخيمتنه": {
        "message_id": 413
    },
    "رف ياعلم": {
        "message_id": 414
    },
    "ماحسبت هالكثر": {
        "message_id": 415
    },
    "ها يسبع الكنطرة": {
        "message_id": 416
    },
    "جاء الاربعين": {
        "message_id": 417
    },
    "هاي الدنية": {
        "message_id": 418
    },
    "الحك يعباس": {
        "message_id": 419
    },
    "عباس الحك": {
        "message_id": 420
    },
    "من هنا": {
        "message_id": 421
    },
    "ايها الصاحب العجل": {
        "message_id": 423
    },
    "قسما": {
        "message_id": 424
    },
    "طش ضعنه": {
        "message_id": 426
    },
    "انا الخليفة": {
        "message_id": 427
    },
    "اويلي من لفت ليله": {
        "message_id": 428
    },
    "يا هاجر": {
        "message_id": 429
    },
    "شلون اصبر على الاه": {
        "message_id": 431
    },
    "طلع شباب من الخيم": {
        "message_id": 432
    },
    "هاك جروح يا مهدينه": {
        "message_id": 433
    },
    "فنة يجي": {
        "message_id": 434
    },
    "ماغفت عيني": {
        "message_id": 435
    },
    "بنات النبي": {
        "message_id": 436
    },
    "مهلا بنات النبي": {
        "message_id": 437
    },
    "يليله يرمله": {
        "message_id": 438
    },
    "عوف المشرعه": {
        "message_id": 439
    },
    "انني عرش النحيب": {
        "message_id": 441
    },
    "علي يشبه علي": {
        "message_id": 442
    },
    "شيخ القادة": {
        "message_id": 443
    },
    "مو انه يا حزن": {
        "message_id": 444
    },
    "مكطوع جف العباس": {
        "message_id": 445
    },
    "دنكت لحسين مهضومه السهام": {
        "message_id": 447
    },
    "مو عليله": {
        "message_id": 448
    },
    "حيهم صاح حيهم": {
        "message_id": 449
    },
    "حيدريون": {
        "message_id": 450
    },
    "لعب جوله بيوم الهد": {
        "message_id": 451
    },
    "اذن الغضب": {
        "message_id": 452
    },
    "يا رايه ليش الوحدج": {
        "message_id": 453
    },
    "سلام وعن بعد": {
        "message_id": 454
    },
    "يغادر كل ملك": {
        "message_id": 455
    },
    "لميت المواكب": {
        "message_id": 456
    },
    "قصة الاكبر": {
        "message_id": 457
    },
    "اكبري اكبري": {
        "message_id": 458
    },
    "اولسنا على الحق": {
        "message_id": 459
    },
    "مملوك الحسين": {
        "message_id": 460
    },
    "فاطمة ملجؤنا": {
        "message_id": 473
    },
    "ياليتنا": {
        "message_id": 462
    },
    "شاهد الخلائق": {
        "message_id": 463
    },
    "مولانا ابا الفضل": {
        "message_id": 464
    },
    "مسلم المهيوب": {
        "message_id": 465
    },
    "الما يعزب للضيف": {
        "message_id": 466
    },
    "ياساقي العشق": {
        "message_id": 467
    },
    "سيد العشق": {
        "message_id": 468
    },
    "احبك يابو فاضل": {
        "message_id": 469
    },
    "توه حله": {
        "message_id": 470
    },
    "لليزور حسين": {
        "message_id": 471
    },
    "هل ترانا": {
        "message_id": 472
    },
    "حيهم يجرحي": {
        "message_id": 474
    },
    "رديتلك": {
        "message_id": 475
    },
    "اية للسائلين": {
        "message_id": 476
    },
    "حرة نسب": {
        "message_id": 477
    },
    "جريمة قتل": {
        "message_id": 478
    },
    "لمحة بصر": {
        "message_id": 480
    },
    "مالي ذنب": {
        "message_id": 481
    },
    "شيعوا نعش الطاهرة المظلومة": {
        "message_id": 482
    },
    "يا اسماء": {
        "message_id": 483
    },
    "زينب هالمسيه": {
        "message_id": 484
    },
    "صلت صلاة الايات": {
        "message_id": 485
    },
    "للنبي محروكه باب": {
        "message_id": 487
    },
    "هل انبا المسمار خير الورى": {
        "message_id": 488
    },
    "قادم بثاري": {
        "message_id": 489
    },
    "اذكر انه": {
        "message_id": 490
    },
    "فارس السبع الشداد": {
        "message_id": 491
    },
    "ليلة وفاتي": {
        "message_id": 493
    },
    "دار الوكت": {
        "message_id": 494
    },
    "فكر انته بمقتلك": {
        "message_id": 495
    },
    "لو فرض": {
        "message_id": 496
    },
    "سواد الطف": {
        "message_id": 497
    },
    "انا العباس ابو النوماس": {
        "message_id": 498
    },
    "وحي الشريعة": {
        "message_id": 499
    },
    "زينب تلطم على الراس": {
        "message_id": 500
    },
    "غضب رب العباد": {
        "message_id": 501
    }
    }
