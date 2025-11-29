from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import ChatParticipantCreator
from telethon.tl.types import ReactionEmoji
import pytz, os, json, asyncio, time, re
import google.generativeai as genai
from typing import Dict, Any
from ABH import *
b = Button.inline("اضغط هنا لعرضها كتابة", data='moneymuch')
ذو_الفقار ="""⢀⢀⢀⠑⢦⡀
⢀⢀⢀⢀⢀⠻⣷⣄
⢀⢀⢀⢀⢀⢀⠘⢿⣷⣄
⢀⢀⢀⢀⢀⢀⢀⠈⢿⣿⣷⣄
⢀⢄⢀⢀⢀⢀⢀⢀⢀⢻⣿⣿⣦⡀
⢀⠈⢿⣦⡀⢀⢀⢀⢀⠈⢿⣿⣿⣷⡄
⢀⢀⢀⢻⣿⣷⣄⢀⢀⢀⠸⣿⣿⣿⣿⣆
⢀⢀⢀⢀⢻⣿⣿⣷⣦⡀⢀⣿⣿⣿⣿⣿⣆
⢀⢀⢀⢀⢀⢻⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⡄
⢀⢀⢀⢀⢀⢀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀
⢀⢀⢀⢀⢀⢀⢀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧
⢀⢀⢀⢀⢀⢀⢀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀
⢀⢀⢀⢀⢀⢀⢀⢀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⣿⠃
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⣿
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⡟
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣾⣿⣿⣿⣿⣿⣿⣿⠁
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣿⣿⣿⣿⣿⣿⣿⡟
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢸⣿⣿⣿⣿⣿⣿⣿⠇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣼⣿⣿⣿⣿⣿⣿⡿
⢀⢀⢀⢀⢀⢀⢀⢀⢀⢠⣿⣿⣿⣿⣿⣿⣿⠇
⢀⢀⢀⢀⢀⢀⢀⢀⢀⣼⣿⣿⣿⣿⣿⣿⡟
⢀⣠⣤⣤⡀⢀⢀⢀⢠⣿⣿⣿⣿⣿⣿⣿⠇
⠸⣿⣿⣿⣷⡀⢀⢀⣾⣿⣿⣿⣿⣿⣿⡿
⢀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇
⢀⢀⢀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄
⢀⢀⢀⢀⢀⢀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀
⢀⢀⢀⢀⢀⢀⣸⣿⣿⣿⣿⣿⣿⠏⢀⢀⢉⣿⣿⣿⣿⡄
⢀⢀⢀⢀⢀⢀⣿⣿⣿⣿⣿⣿⠛⢀⢀⢀⣿⣿⠿⠁
⢀⢀⢀⢀⢀⣸⣿⣿⣿⣿⣿⣿⡇
⢀⢀⢀⢀⢀⣿⣿⣿⣿⣿⣿⣍
⢀⢀⢀⢀⣼⣿⣿⣿⣿⣿⡟⠋
⢀⢀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣆
⢀⢀⢀⢿⣿⣿⣿⣿⣿⣿⣿⣿
⢀⢀⢀⢀⠙⠿⠿⣿⡿⠿"""
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
actions = [
    'يوتيوب',
    'تقييد',
    'ردود',
    'تنظيف',
    'تحذير', 
    'ميم'
    ]
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
async def to(e):
    try:
        reply = await e.get_reply_message()
        if reply:
            return reply
        args = e.pattern_match.group(1)
        target = args.strip() if args else None
        if target and target.isdigit():
            return await ABH.get_entity(int(target))
        if target:
            if target.startswith('@'):
                target = target[1:]
            elif target.startswith('https://t.me/'):
                target = target.replace('https://t.me/', '')
            try:
                entity = await ABH.get_entity(target)
                return entity
            except Exception as ex:
                await hint(f"❌ خطأ أثناء جلب المستخدم: {ex}")
                return None
        return None
    except Exception as ex:
        await hint(f"⚠️ حدث خطأ أثناء معالجة الهدف: {ex}")
        return None
async def auth(event, x=False, to=None):
    chat_id = event.chat_id
    if to:
        user_id = to
    elif x:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id if reply_msg else None
    else:
        user_id = event.sender_id
    if user_id == wfffp:
        return "المطور الاساسي"
    if await is_owner(chat_id, user_id):
        return "المالك"
    devers = save(None, "secondary_devs.json")
    if str(user_id) in devers.get(str(chat_id), []):
        participant = await ABH(GetParticipantRequest(channel=int(chat_id), participant=int(user_id)))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            mention_text = await mention(event)
            await event.reply(f"📉 تم تنزيل {mention_text} من قائمة المطورين الثانويين \n⚠️ السبب: ليس لديه صلاحيات مشرف.")
            dev = f"{event.chat_id}:{user_id}"
            delsave(dev, filename="secondary_devs.json")
        else:
            return "المطور الثانوي"
    if is_assistant(chat_id, user_id):
        participant = await ABH(GetParticipantRequest(channel=int(chat_id), participant=int(user_id)))
        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            mention_text = await mention(event)
            await event.reply(f"📉 تم تنزيل {mention_text} من قائمة المعاونين \n⚠️ السبب: ليس لديه صلاحيات مشرف.")
            data = load_auth()
            if str(chat_id) in data and user_id in data[str(chat_id)]:
                data[str(chat_id)].remove(user_id)
                save_auth(data)
        else:
            return "المعاون"
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
async def send(e, m, b=None):
    c = e.chat_id
    l = await LC(str(c))
    if not l:
        return
    await ABH.send_message(l, m, buttons=b)
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
    d = create('res.json')
    if المصدر is None:
        return d
    if isinstance(المصدر, str) and ":" in المصدر:
        parts = المصدر.split(":")
        chat_id, user_id = str(parts[0]), str(parts[1])
    else:
        chat_id, user_id = المصدر.chat_id, المصدر.sender_id
    if chat_id not in d:
        d[chat_id] = {}
    end_time = int(time.time()) + (t or 20)
    d[chat_id][user_id] = end_time
    with open('res.json', 'w', encoding='utf-8') as file:
        json.dump(d, file, ensure_ascii=False, indent=4)
    if stop:
        return d
    now = int(time.time())
    rights = ChatBannedRights(
        until_date=now + (t or 20),
        send_messages=True
    )
    await ABH(EditBannedRequest(channel=int(chat_id), participant=int(user_id), banned_rights=rights))
    return d
def delres(chat_id=None, user_id=None):
    create('res.json')
    with open('res.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    if chat_id and user_id:
        chat_id = str(chat_id)
        user_id = str(user_id)
    if chat_id in data and user_id in data[chat_id]:
        del data[chat_id][user_id]
        if not data[chat_id]:
            del data[chat_id]
        with open('res.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    return False
async def info(e, msg_type):
    f = 'info.json'
    if not os.path.exists(f):
        create(f)
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        content = re.sub(r"[\x00-\x1F\x7F]", "", content)
        content = re.sub(r",\s*([\]}])", r"\1", content)
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}
    chat = str(e.chat_id)
    user_id = str(e.sender_id)
    if chat not in data:
        data[chat] = {}
    if user_id not in data[chat]:
        data[chat][user_id] = {
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
    if msg_type is None:
        return data[chat][user_id]
    if msg_type not in data[chat][user_id]:
        data[chat][user_id][msg_type] = 0
    data[chat][user_id][msg_type] += 1
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return data[chat][user_id]
WHITELIST_FILE = "whitelist.json"
whitelist_lock = asyncio.Lock()
async def ads(group_id: int, user_id: int) -> None:
    async with whitelist_lock:
        data = {}
        if os.path.exists(WHITELIST_FILE):
            try:
                with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        group_key = str(group_id)
        group_list = data.get(group_key, [])
        if user_id not in group_list:
            group_list.append(user_id)
            data[group_key] = group_list
            with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
async def lw(group_id: int) -> list[int]:
    async with whitelist_lock:
        if not os.path.exists(WHITELIST_FILE):
            return []
        try:
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return []
        return data.get(str(group_id), [])
CONFIG_FILE = "vars.json"
config_lock = asyncio.Lock()
async def configc(group_id: int, hint_cid=None) -> None:
    config = create(CONFIG_FILE)
    if hint_cid is None:
        if str(group_id) in config:
            del config[str(group_id)]
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        return    
    config[str(group_id)] = {"hint_gid": int(hint_cid)}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
async def LC(group_id: int) -> int | None:
    async with config_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                return None
            group_config = config.get(str(group_id))
            if group_config and "hint_gid" in group_config:
                return int(group_config["hint_gid"])
        return None
async def link(e, text=False):
    chat = e.chat_id
    id = e.id
    c = str(chat).replace('-100', '')
    x = f'https://t.me/c/{c}/{id}'
    if text:
        return x
    chat = await e.get_chat()
    name = getattr(chat, "title", "محادثة خاصة")
    return f"[{name}]({x})"
async def username(event, x=False):
    if x:
        r = await event.get_reply_message()
        if not r:
            return 'مالي خلك روح جيبه انت'
        return r.sender.username
    if event.sender and event.sender.username:
        return event.sender.username
    s = await event.get_sender()
    if getattr(s, "usernames", None):
        for u in s.usernames:
            if u and u.username:
                return u.username
    return None
async def try_forward(event):
    gidvar = await LC(event.chat_id)
    if not gidvar:
        return False
    try:
        await ABH.forward_messages(
            entity=int(gidvar),
            messages=event.id,
            from_peer=event.chat_id
        )
    except:
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
        await hint(f"❌ خطأ أثناء إضافة رد الفعل: {e}")
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
group = -1001784332159
hint_gid = -1002168230471
bot = "Anymous"
wfffp = 1910015590
async def hint(e):
    await ABH.send_message(wfffp, str(e))
async def mention(event):
    name = getattr(event.sender, 'first_name', None) or 'غير معروف'
    user_id = event.sender_id
    return f"[{name}](tg://user?id={user_id})"
async def ment(entity):
    try:
        if hasattr(entity, "id") and hasattr(entity, "first_name"):
            name = getattr(entity, "first_name", "غير معروف")
            user_id = entity.id
            return f"[{name}](tg://user?id={user_id})"
        if hasattr(entity, "sender_id"):
            sender = entity.sender or await entity.get_sender()
            name = getattr(sender, "first_name", "غير معروف")
            user_id = sender.id
            return f"[{name}](tg://user?id={user_id})"
        if hasattr(entity, "id"):
            name = getattr(entity, "first_name", "غير معروف")
            user_id = entity.id
            return f"[{name}](tg://user?id={user_id})"
        return "غير معروف"
    except Exception:
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
    ('سورة الفاتحة',): '1',
    ('سورة البقرة',): '2',
    ('سورة آل عمران', 'سورة ال عمران'): '3',
    ('سورة النساء',): '4',
    ('سورة المائده', 'سورة المائدة'): '5',
    ('سورة الأنعام', 'سورة الانعام'): '6',
    ('سورة الأعراف', 'سورة الاعراف'): '7',
    ('سورة الأنفال', 'سورة الانفال'): '8',
    ('سورة التوبة',): '9',
    ('سورة يونس',): '10',
    ('سورة هود',): '11',
    ('سورة يوسف',): '12',
    ('سورة الرعد',): '13',
    ('سورة ابراهيم', 'سورة إبراهيم'): '14',
    ('سورة الحجر',): '15',
    ('سورة النحل',): '16',
    ('سورة الاسراء', 'سورة الإسراء'): '17',
    ('سورة الكهف',): '18',
    ('سورة مريم',): '19',
    ('سورة طه',): '20',
    ('سورة الانبياء', 'سورة الأنبياء'): '21',
    ('سورة الحج',): '22',
    ('سورة المؤمنون', 'سورة المومنون'): '23',
    ('سورة الفرقان',): '24',
    ('سورة النور',): '25',
    ('سورة الشعراء',): '26',
    ('سورة العنكبوت',): '27',
    ('سورة النمل',): '28',
    ('سورة القصص',): '29',
    ('سورة الروم',): '30',
    ('سورة لقمان',): '31',
    ('سورة السجدة',): '32',
    ('سورة الأحزاب', 'سورة الاحزاب'): '33',
    ('سورة سبأ', 'سورة سبا'): '34',
    ('سورة فاطر',): '35',
    ('سورة يس',): '36',
    ('سورة الصافات',): '37',
    ('سورة ص',): '38',
    ('سورة الزمر',): '39',
    ('سورة غافر',): '40',
    ('سورة فصلت',): '41',
    ('سورة الشورى',): '42',
    ('سورة الزخرف',): '43',
    ('سورة الدخان',): '44',
    ('سورة الجاثية',): '45',
    ('سورة الاحقاف', 'سورة الأحقاف'): '46',
    ('سورة الفتح',): '47',
    ('سورة محمد',): '48',
    ('سورة الحجرات',): '49',
    ('سورة الذاريات',): '50',
    ('سورة ق',): '51',
    ('سورة النجم',): '52',
    ('سورة الطور',): '53',
    ('سورة القمر',): '54',
    ('سورة الرحمن',): '55',
    ('سورة الواقعة',): '56',
    ('سورة الحديد',): '57',
    ('سورة المجادلة',): '58',
    ('سورة الحشر',): '59',
    ('سورة الممتحنة',): '60',
    ('سورة الصف',): '61',
    ('سورة الجمعة',): '62',
    ('سورة المنافقون',): '63',
    ('سورة التغابن',): '64',
    ('سورة الطلاق',): '65',
    ('سورة التحريم',): '66',
    ('سورة الملك',): '67',
    ('سورة القلم',): '68',
    ('سورة الحاقة',): '69',
    ('سورة المعارج',): '70',
    ('سورة نوح',): '71',
    ('سورة الجن',): '72',
    ('سورة المزمل',): '73',
    ('سورة المدثر',): '74',
    ('سورة القيامة',): '75',
    ('سورة الإنسان', 'سورة الانسان'): '76',
    ('سورة المرسلات',): '77',
    ('سورة النبا', 'سورة النبأ'): '80',
    ('سورة النازعات',): '78',
    ('سورة عبس',): '79',
    ('سورة التكوير',): '81',
    ('سورة الانفطار', 'سورة الإنفطار'): '82',
    ('سورة المطففين',): '83',
    ('سورة الانشقاق',): '84',
    ('سورة البروج',): '85',
    ('سورة الطارق',): '86',
    ('سورة الاعلى', 'سورة الأعلى'): '87',
    ('سورة الغاشية',): '88',
    ('سورة الفجر',): '89',
    ('سورة البلد',): '90',
    ('سورة الشمس',): '91',
    ('سورة الليل',): '92',
    ('سورة الضحى',): '93',
    ('سورة الشرح',): '94',
    ('سورة التين',): '96',
    ('سورة العلق',): '95',
    ('سورة القدر',): '97',
    ('سورة البينة',): '98',
    ('سورة الزلزلة',): '99',
    ('سورة العاديات',): '100',
    ('سورة القارعة',): '101',
    ('سورة التكاثر',): '102',
    ('سورة العصر',): '103',
    ('سورة الهمزة',): '104',
    ('سورة الفيل',): '105',
    ('سورة قريش',): '106',
    ('سورة الماعون',): '107',
    ('سورة الكوثر',): '108',
    ('سورة الكافرون',): '109',
    ('سورة النصر',): '110',
    ('سورة المسد',): '111',
    ('سورة الاخلاص', 'سورة الإخلاص'): '112',
    ('سورة الفلق',): '113',
    ('سورة الناس',): '114',
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
