from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import ChatParticipantCreator
from telethon.tl.types import ReactionEmoji
from telethon import Button
import pytz, os, json, asyncio, time, re
# import google.generativeai as genai
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
لطميات = {
    "من هو العباس  حيدر البياتي ليلة ٧ محرم": {
        "message_id": 50
    },
    "هلا ب اربعينه محمد الجنامي  المشايه 1445 هـ 2023 م": {
        "message_id": 51
    },
    "جداه الرادود باسم الكربلائي": {
        "message_id": 52
    },
    "عدلين ميتين يمك  الملا محمد باقر الخاقاني - عزاء حسينية الحاج ع": {
        "message_id": 53
    },
    "حروبك ياعلي  علي ياحيدر  حيدر البياتي - جديد شهادة امير المؤ": {
        "message_id": 54
    },
    "راية العباس    حسين والي اللامي": {
        "message_id": 55
    },
    "غضب الله  الرادود حيدر البياتي ليلة ٧ محرم الحرام 1446هـ - 2": {
        "message_id": 56
    },
    "اعصار العباس  كرار ابو غنيم  موكب شعراء ورواديد النجف ليله 7": {
        "message_id": 57
    },
    "معكم معكم - with you  الملا محمد بوجبارة - الملا محمود اسيري": {
        "message_id": 58
    },
    "بندرية خيرة الله من الخلق ابي  محمد عامر الاسدي  محرم الحرام": {
        "message_id": 59
    },
    "قرة عين  الرادود خضر عباس - هيئة نهج علي - محرم الحرام 1446 هـ": {
        "message_id": 60
    },
    "ليالي الجروح  الملا محمد باقر الخاقاني  هيئة الحسن المجتبى عل": {
        "message_id": 61
    },
    " موعود الك  الرادود سيد محمد الحسيني": {
        "message_id": 62
    },
    "سيد سلام الحسيني  الى الوداع سيدي ": {
        "message_id": 63
    },
    "نصراً من الله وفتح قريبll ملا مجتبى الكعبي ll موكب عشق علي -البص": {
        "message_id": 64
    },
    "نزله نجفيه - يبن عم المصطفى وياساعده - السيد مرتضى الصافي ( ليلة": {
        "message_id": 66
    },
    "عباس بونينك  مسلم الوائلي  هيئة وحسينية باب الزهراء  محرم الح": {
        "message_id": 67
    },
    "يحيى البنداوي \"امنة البيوت بيده وطلعنه\" طلعت زلمنة #حصريا (offic": {
        "message_id": 68
    },
    "رحلة  قحطان البديري  ( مشاية الاربعين ) 1444": {
        "message_id": 69
    },
    "ابد والله لن ننسى حسينا": {
        "message_id": 70
    },
    "ها يمهدي  الرادود باسم الكربلائي": {
        "message_id": 73
    },
    "ها عليهم  احمد الباوي": {
        "message_id": 74
    },
    "ابد والله يا زهراء ما ننسى حسيناه-باسم الكربلائي 1432": {
        "message_id": 75
    },
    "شد الثامه  محمد الجنامي  محرم الحرام 1445": {
        "message_id": 76
    },
    "لزمة علينه المشرعهملا علي الوائلي وملا مسلم الوائلي  هيئة313 مح": {
        "message_id": 78
    },
    "فروا الى الحسين  #علي_سعيد_الوائلي _قصيدة استقبال محرم الحرام 2": {
        "message_id": 83
    },
    "صوت احساس وي عباس جفك زمزم يا وفاي جيب الماي": {
        "message_id": 84
    },
    "الساقي الرادود سيف الذهبيالذاكر مهند طالب": {
        "message_id": 85
    },
    "يا نجمه  الرادود باسم الكربلائي": {
        "message_id": 86
    },
    "يلابس ثياب العرس وين العرس  بندرية  سيد سلام الحسيني": {
        "message_id": 87
    },
    "ذوله الولدملا علي الوائليموكب شباب علي الاكبر": {
        "message_id": 88
    },
    "شيخ النشامه  الرادود خضر عباس - هيئة نهج علي - جديد قصيدة للعبا": {
        "message_id": 89
    },
    "ام وهب  الملا حيدر الفريجي  هيئة جبل الصبر زينب (ع)": {
        "message_id": 90
    },
    "الرادود خضر عباس  حسينا  1445 هـ": {
        "message_id": 91
    },
    "راياتنا  شهادة الرسول الاعظم ص  الرادود خضر عباس": {
        "message_id": 92
    },
    "ما بيننا ايات  الحاج باسم الكربلائي": {
        "message_id": 95
    },
    "ملكك وانت ديني  سيد فاقد الموسوي  1445 هـ": {
        "message_id": 96
    },
    "عيد الغدير بنكهة اهوازية": {
        "message_id": 97
    },
    "روحي  الرادود باسم الكربلائي": {
        "message_id": 98
    },
    "مشوار الحب - الرادود باسم الكربلائي": {
        "message_id": 99
    },
    "اطوي الارض  الحاج باسم الكربلائي": {
        "message_id": 100
    },
    "دنيا  باسم الكربلائي": {
        "message_id": 101
    },
    "يالراهب برسمه  الرادود باسم الكربلائي": {
        "message_id": 102
    },
    "طلعت يحسين المشاية  مشتركة ، قحطان البديري ، حسن الكطراني  قصي": {
        "message_id": 103
    },
    "شايل اصرار هو الدرس من مدرسه حيدر علمه جبير وما يشيل الصف كرار…": {
        "message_id": 104
    },
    "قمر الال هلا  الحاج باسم الكربلائي": {
        "message_id": 105
    },
    "صورة علي  الملا علي الساعدي": {
        "message_id": 106
    },
    "ام الوجود  يحيى عفارة 1444 هـ": {
        "message_id": 107
    },
    "عصابة امي الماطاحت من لفلفتها ، فرقة الانشاد الاهوازية ، حسن نصر": {
        "message_id": 108
    },
    "خطة حرب": {
        "message_id": 109
    },
    "كلبي ضامي  مسلم الوائلي  عزاء لواء الحسين 1441": {
        "message_id": 112
    },
    "سامحيني  الرادود باسم الكربلائي": {
        "message_id": 113
    },
    "شيخ الخدام موسى البولاني": {
        "message_id": 116
    },
    "زينب لفت - الحاج باسم الكربلائي": {
        "message_id": 117
    },
    "نزله  الرادود احمد الفتلاوي": {
        "message_id": 118
    },
    "حديث الموت  ملا مجتبى الكعبي  هيئة حرم الله  مشاية الاربعي": {
        "message_id": 119
    },
    "جبنالك ماي ويانه  ملا علي الوائلي  محرم 1446 هجري": {
        "message_id": 120
    },
    "اول خليفة  علي سعيد الوائلي": {
        "message_id": 122
    },
    "يا ساقي الماي - ملا باسم الكربلائي المونتاج الكامل hd": {
        "message_id": 123
    },
    "شكراً جزيلاً عباس  ملا مصطفى السوداني": {
        "message_id": 124
    },
    "بندرية  الرادود خضر عباس": {
        "message_id": 125
    },
    "هوسات العباس": {
        "message_id": 126
    },
    "هوسات الموت  الرادود حيدر البياتي والشاعر مصطفى العيساوي": {
        "message_id": 127
    },
    "طبت عراضه كوم طب اعليهم _جبارالحريشاوي_ هوسات العباس  _كوم اعرض ": {
        "message_id": 128
    },
    "مجانينه  محمد الجنامي": {
        "message_id": 129
    },
    "مرتضى حرب  مات الورد  الليالي الفاطمية 1445 هجري": {
        "message_id": 130
    },
    "ياكلبي كافي ولم العتاب  مسلم الوائلي  هيئة وارث الائمة 1442": {
        "message_id": 132
    },
    "حبست دموع عيني  محمد الجنامي": {
        "message_id": 133
    },
    "سد عينك  سيد فاقد الموسوي  1445 هـ": {
        "message_id": 134
    },
    "شد عليهم  الرادود محمد الموسوي": {
        "message_id": 135
    },
    "هذا كافل زينب   محمد الحجيرات  محرم ١٤٤١ هـ": {
        "message_id": 137
    },
    "عباس لو علي  الرادود حيدر البياتي": {
        "message_id": 138
    },
    "ناحر الحومه  احمد الباوي 1446 هـ": {
        "message_id": 139
    },
    "خجلانه هواي  الرادود باسم الكربلائى": {
        "message_id": 140
    },
    "قارورة  الرادود باسم الكربلائي": {
        "message_id": 141
    },
    "النوايب صوبني": {
        "message_id": 143
    },
    "وليدي القمر  الرادود باسم الكربلائي": {
        "message_id": 144
    },
    "بجيتك  ملا مجتبى الكعبي  موكب احزان السماوه  محرم ١٤٤٦هـ ٢": {
        "message_id": 145
    },
    "مرت سنة ونص  الرادود باسم الكربلائي": {
        "message_id": 146
    },
    "اين استقرت يا ابو صالح  ملا فاضل الكربلائي  1437 2015": {
        "message_id": 147
    },
    "علم عالقاع يا حيدر يا بويه ومنك اتعذر   باسم الكربلائي": {
        "message_id": 149
    },
    "اشهدوله  الرادود باسم الكربلائي": {
        "message_id": 151
    },
    "ذوله خوتهم صدگ  مسلم الوائلي  1446هـ": {
        "message_id": 153
    },
    "للمشرعه تعنيت  سيد سلام الحسيني  محرم الحرام 1446 ه‍  عزاء ال": {
        "message_id": 154
    },
    "الخدم بحماك  سيد سلام الحسيني [ محرم الحرام 1446 هجري ] عزاء حس": {
        "message_id": 155
    },
    "هله يا هيبة الساده الرادود حيدر البياتي #جديد2024": {
        "message_id": 156
    },
    "نصر الله الرادود حيدر البياتي": {
        "message_id": 157
    },
    "كلشي مات  ملا علي الوائلي  عزاء هيئة ملك المشرعه": {
        "message_id": 158
    },
    "لاترحلي عباس عجيد العامريماتم الشبيه الاشبه علي الاكبر بغدا": {
        "message_id": 160
    },
    "ان وعد الله حق  ملا مجتبى الكعبي  video cl  اصدار _١٤٤٦هـ ": {
        "message_id": 161
    },
    "سارح خيالي  الحاج باسم الكربلائي": {
        "message_id": 162
    },
    "يا زينب  الرادود باسم الكربلائي": {
        "message_id": 163
    },
    "هاي الزلم  حسن خريبط 2024 حصريا": {
        "message_id": 164
    },
    "تسبيحة عشاق  الرادود باسم الكربلائي": {
        "message_id": 165
    },
    "سلام الله  الرادود باسم الكربلائي": {
        "message_id": 166
    },
    "يا باب الحوائج حاجتي يمك  باسم الكربلائي  استشهاد الامام الكاظ": {
        "message_id": 167
    },
    "سيد الاحساس": {
        "message_id": 168
    },
    "الفصول الاربعة  الرادود باسم الكربلائي": {
        "message_id": 169
    },
    "طبع الشمع  الرادود باسم الكربلائي": {
        "message_id": 170
    },
    "تدري لو متدري  الرادود باسم الكربلائي": {
        "message_id": 171
    },
    "سامحني  الحاج باسم الكربلائي": {
        "message_id": 172
    },
    "قلب مجروح  الرادود باسم الكربلائي": {
        "message_id": 173
    },
    "ياحي الله الاكبر  الرادود باسم الكربلائي": {
        "message_id": 174
    },
    "قاللها صار  الرادود باسم الكربلائي": {
        "message_id": 176
    },
    "نتيجة غيبتك  الرادود باسم الكربلائي": {
        "message_id": 177
    },
    "انا من انا  الرادود باسم الكربلائى": {
        "message_id": 178
    },
    "ام البنين تنادي الكعبيحسينية ضامن الغزال عليه السلامم": {
        "message_id": 179
    },
    "نزلة نجفية ": {
        "message_id": 180
    },
    " زينب ردت من الشام  1445 هـ": {
        "message_id": 205
    },
    "ملك الموت  الرادود باسم الكربلائي": {
        "message_id": 184
    },
    "عينك  الرادود باسم الكربلائي": {
        "message_id": 185
    },
    "لا فتى الا علي  الرادود باسم الكربلائي": {
        "message_id": 186
    },
    "حياتي  الرادود باسم الكربلائي": {
        "message_id": 187
    },
    "رحل كل غالي  الرادود باسم الكربلائي": {
        "message_id": 188
    },
    "ندمان وراجعلك  عباس عجيد العامري  هيئة حفيد الامام الكاظم اب": {
        "message_id": 189
    },
    "منين اجيب الماي  الرادود باسم الكربلائي": {
        "message_id": 190
    },
    "انا الهلال  الرادود باسم الكربلائي": {
        "message_id": 191
    },
    "حيدر من وصلها  الرادود باسم الكربلائي": {
        "message_id": 192
    },
    "لا تتاخر عليه  الرادود باسم الكربلائى": {
        "message_id": 193
    },
    "يالمهدي  باسم الكربلائي": {
        "message_id": 195
    },
    "تذكرة عشق": {
        "message_id": 196
    },
    "الخير كله بخدمة حسين - الملا علي بوحمد  ليلة 2 محرم 1441 هـ": {
        "message_id": 197
    },
    "طلع شباب من الخيم  عباس عجيد العامري  موكب خوة العباس (ع) - ": {
        "message_id": 198
    },
    "اضحاب الحسين  الرادود باسم الكربلائي": {
        "message_id": 199
    },
    "يا طود الصبر  الحاج باسم الكربلائي": {
        "message_id": 200
    },
    "ياحيدر بباب الدار  الرادود باسم الكربلائي": {
        "message_id": 201
    },
    "اللهم عجل - الحاج باسم الكربلائي": {
        "message_id": 202
    },
    "ليلة وداع  الرادود باسم الكربلائي": {
        "message_id": 203
    },
    "عاشق وحسيني  الرادود باسم الكربلائي": {
        "message_id": 204
    },
    "شال الطف عباس  الملا مرتضى الحميداوي - عزاء هيئة رماد الخيام - ": {
        "message_id": 206
    },
    "مولاتي يا مولاتي": {
        "message_id": 207
    },
    "يا حادي الضعن ريض الرادود عباس الاسحاقي": {
        "message_id": 208
    },
    "مظلوم حسين جانم  قسما بالله داحي الارض خلاق السماوات عربي  فا": {
        "message_id": 209
    },
    "هلا بك  الحاج باسم الكربلائي": {
        "message_id": 210
    },
    "علي حيدر يكرار  دانيال بوجبارة  1444 هـ": {
        "message_id": 211
    },
    "جف اليصافح  باسم الكربلائي": {
        "message_id": 213
    },
    "كل شي عباس  محمد الحجيرات  محرم 1441هـ": {
        "message_id": 214
    },
    "سامع اذ حب الگلب  ملا مجتبى الكعبي  موكب سيد الماء  ١٤٤٦هـ": {
        "message_id": 215
    },
    "الم سبي حرم  الرادود باسم الكربلائي": {
        "message_id": 216
    },
    "انا بنت الهتف جبريل  الرادود باسم الكربلائي": {
        "message_id": 217
    },
    "شور  مات الولد مات   الملا كرار الكربلائي ": {
        "message_id": 218
    },
    "ضي منحرك (ميمر كربلائي) - علي بوحمد  dhay manharak - ali bouham": {
        "message_id": 219
    },
    " ها هو القاسم  سيد محمد الحسيني": {
        "message_id": 220
    },
    "بين المهدي والعباس  الرادود باسم الكربلائي": {
        "message_id": 221
    },
    "مرتضى حرب - كولو علي": {
        "message_id": 222
    },
    "همت و الشوق جنني باسم الكربلائي #باسم_الكربلائي": {
        "message_id": 223
    },
    "كل مايجي اليل  سيد فاقد الموسوي  video 2023": {
        "message_id": 224
    },
    "ليث المعركة   محمد الخياط  video clip 2018": {
        "message_id": 225
    },
    "الماتم ثقافتنا  باسم الكربلائي": {
        "message_id": 226
    },
    "ياعلي مدد - باسم الكربلائي": {
        "message_id": 227
    },
    "نسل حيدرم  الرادود محمد الحجيرات  مونتاج جديد  محرم 1438": {
        "message_id": 228
    },
    "يا فاطمة يم الحسن  الملا عمار الكناني - جامع ذي الفقار- العراق ": {
        "message_id": 229
    },
    "يا بوفاضل  الرادود باسم الكربلائي": {
        "message_id": 231
    },
    "براءة العشق  الرادود باسم الكربلائي": {
        "message_id": 232
    },
    "يخيمات  الرادود عمار الكناني  محرم -١٤٣٩": {
        "message_id": 233
    },
    "مصحفنه خط احمر  محمد الحلفي  مجالس محرم 1445هـ 2023مـ   2023 ": {
        "message_id": 234
    },
    "زينب وين  الحاج باسم الكربلائي": {
        "message_id": 235
    },
    "محمد الحجيرات  الكوثرية  2021-1442": {
        "message_id": 236
    },
    "يوم   باسم الكربلائي": {
        "message_id": 237
    },
    "نمشي مع الحجة  باسم الكربلائي": {
        "message_id": 238
    },
    "اجه الموت  الرادود باسم الكربلائي": {
        "message_id": 239
    },
    "رجعت ادين الطغيان  الرادود باسم الكربلائي": {
        "message_id": 240
    },
    "تصد للدرب عيني  سيد سلام الحسيني  [ شهادة مولاتي ام البنين عليه": {
        "message_id": 241
    },
    "ظلم كسر ضلع  الرادود باسم الكربلائي": {
        "message_id": 242
    },
    "سلطان الرفض _ الرادود كرار ابو غنيم والرادود حيدر البياتي": {
        "message_id": 243
    },
    "قيامه كربله  الرادود محمد باقر الخاقاني  شوط كربلائي": {
        "message_id": 244
    },
    "زينب نادت السجاد  محمد باقر الخاقاني ( شوط كربلائي )": {
        "message_id": 246
    },
    "انشوده المهدي قادم ناصر للثوار  عباس عدنان الحسناوي": {
        "message_id": 247
    },
    "يسلطان المشاعر ملا حسن خريبط": {
        "message_id": 248
    },
    "شوط كربلائي باسم الكربلائي": {
        "message_id": 249
    },
    "نحن لانهزم ومنا عطاء الدم \" غزة الصمود والعزة \"": {
        "message_id": 250
    },
    "اوبريت الله في الساحة - حصرياً 2024": {
        "message_id": 251
    },
    "اوبريت المد الشيعي 2015 علي الدلفي مصطفى الربيعي مهد العبودي غسا": {
        "message_id": 252
    },
    "اوبريت هيبة هاشم   فتية الكميل": {
        "message_id": 253
    },
    "قتال العرب  سيد فاقد الموسوي  عزاء هيئة لواء زينب - قصر العب": {
        "message_id": 255
    },
    "راعي الصيت  محمد الفاطمي  هيئة غريب طوس 1445 هـ": {
        "message_id": 265
    },
    "سمع الله لمن قال علي ملا مجتبى الكعبي": {
        "message_id": 257
    },
    "انا ما املك وجودي": {
        "message_id": 258
    },
    "احنا خوالو حيدر الفريجي_ محرم الحرام 1446": {
        "message_id": 259
    },
    "بندرية عرس بارض الطفوف  سيد سلام الحسيني [ محرم الحرام 1446 هجر": {
        "message_id": 260
    },
    "سالفتي نحیب  محمد باقر الخاقاني  جديد محرم 14432021": {
        "message_id": 261
    },
    "بندرية مناجاة الحسين  الرادود ميرزا حيدر الابراهيمي - حسينية عز": {
        "message_id": 262
    },
    "هذا ابن فاطمة  الرادود حسين الجابري - ليالي شهادة السجاد - محرم": {
        "message_id": 263
    },
    "في درب فاطمة  حسين خيرالدين": {
        "message_id": 264
    },
    "علي يامن قلعت الباب  الرادود باسم الكربلائي": {
        "message_id": 266
    },
    "يمه اطمنج عليه  الرادود باسم الكربلائي": {
        "message_id": 267
    },
    "وسط كلبي شحلاتك ll الرادود مهدي العبادي ll الشاعر ايوب الشغانبي": {
        "message_id": 268
    },
    "مسلم يا ربات حسين  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء ": {
        "message_id": 269
    },
    "تربات البدو i حيدر الفريجي i محرم 1446 هـ": {
        "message_id": 270
    },
    "گوم يابو الجود   الملا محمد باقر الخاقاني هيئة سيدة الوجود (ع)": {
        "message_id": 271
    },
    "سلام يا مهدي  محمد غلوم": {
        "message_id": 272
    },
    "سلام يا مهدي  الرادود احمد الفتلاوي": {
        "message_id": 274
    },
    "اجمل ساقي  عباس عجيد العامري  موكب وحسينية الزهراء - البصرة ": {
        "message_id": 276
    },
    "صولة العباس  نزال بندري  الرادود ايمن السعدي  محرم الحرام 144": {
        "message_id": 277
    },
    "حي الله عباس  ميرزا محمد الخياط  محرم 1438": {
        "message_id": 278
    },
    "ربت زلم  الرادود حسين الزغير الكربلائي": {
        "message_id": 279
    },
    "ريت السافر يعود  الرادود باسم الكربلائي": {
        "message_id": 280
    },
    "يالمدلل يعبد الله  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء ": {
        "message_id": 281
    },
    "يا ام البنين  الرادود باسم الكربلائي": {
        "message_id": 282
    },
    "اعادة نشر  لحسين انتمائي  محمد الحجيرات": {
        "message_id": 283
    },
    "عقلي بجنون  الرادود باسم الكربلائي": {
        "message_id": 284
    },
    "يا با الفضل  الرادود باسم الكربلائي": {
        "message_id": 285
    },
    "بالله يا نهر  الرادود باسم الكربلائي": {
        "message_id": 286
    },
    "يا نبضا لاحساسي  الرادود باسم الكربلائي": {
        "message_id": 287
    },
    "الموت ارتبك  الرادود باسم الكربلائي": {
        "message_id": 288
    },
    "عد لي حبيبي  نشيد في حق الامام المهدي (عج)  حسن القدسي": {
        "message_id": 289
    },
    "ائمتي وسادتي اثنا عشر  محمد محيدلي": {
        "message_id": 290
    },
    "حب بلا خصام  الرادود باسم الكربلائى": {
        "message_id": 291
    },
    "قمر كربلاء  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء الناصري": {
        "message_id": 292
    },
    "ناذر سنيني  الرادود باسم الكربلائي": {
        "message_id": 293
    },
    "مثل طبع النسر طبعي 1  باسم الكربلائي": {
        "message_id": 294
    },
    "سلام عن بعد  الملا محمد باقر الخاقاني - عزاء هيئة لواء الزهراء ": {
        "message_id": 295
    },
    "حصن خيبر  مجتبى الكعبي  مضيف زمن الغيبة  video new": {
        "message_id": 296
    },
    "امنياتي  الرادود باسم الكربلائي": {
        "message_id": 297
    },
    "اوبريت فرحة السادة  فتية الكميل  سلسلة حضرة القائد": {
        "message_id": 298
    },
    "كون يامرنا سيد على السيستاني": {
        "message_id": 299
    },
    "نزله عزاء النجف الاشرف  الاربعين 1440  الرادود هادي مريطي مونتا": {
        "message_id": 300
    },
    "حيرة حسين ": {
        "message_id": 379
    },
    "توكل على الله وللنهر صول يضرغام ( نزلة نجفية ثلاث دگات) اللطم يش": {
        "message_id": 304
    },
    "اكتب عذابي  الرادود باسم الكربلائي": {
        "message_id": 305
    },
    "حراس العقيدة  الشيخ حسين الاكرف": {
        "message_id": 306
    },
    "كليم الحسين باسم الكربلائي اصدار كليم الحسين النسخة الاصلية": {
        "message_id": 307
    },
    "طفح الدمع وقال انت قوس ام هلال باسم الكربلائي": {
        "message_id": 308
    },
    "بروحي - ام المؤمنين خديجة  باسم الكربلائي": {
        "message_id": 309
    },
    "يكرهوني واحبك  الرادود باسم الكربلائي": {
        "message_id": 310
    },
    "نوح و دمع  باسم الكربلائي _ اصدار 1426 هـ": {
        "message_id": 311
    },
    "تركنا الخلق طرا  الحاج باسم الكربلائي": {
        "message_id": 312
    },
    "امير الجمال  حسن الكطراني #جديد2025-1446هـ": {
        "message_id": 313
    },
    "رايح الغالي  الرادود باسم الكربلائي": {
        "message_id": 430
    },
    "ما ذنب طفلي  الرادود باسم الكربلائي": {
        "message_id": 315
    },
    "الوداع  الرادود باسم الكربلائي": {
        "message_id": 316
    },
    "ادعي يا زينب  الرادود باسم الكربلائي": {
        "message_id": 317
    },
    "ما ندري  الرادود باسم الكربلائي": {
        "message_id": 318
    },
    "والله افنيها  الرادود باسم الكربلائي": {
        "message_id": 319
    },
    "حي على العزاء  الرادود باسم الكربلائي": {
        "message_id": 320
    },
    "تجارة لن تبور  الحاج باسم الكربلائي": {
        "message_id": 321
    },
    "ما اشوف بعيني  الرادود باسم الكربلائي": {
        "message_id": 322
    },
    "جل جلاله  الرادود باسم الكربلائي": {
        "message_id": 323
    },
    "المشكاه السبعه  الرادود مجتبى الكعبي  الذاكر حسن الشامي": {
        "message_id": 324
    },
    "خطب العباس  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء الناصري": {
        "message_id": 325
    },
    "الغيرة الهاشمية  سيد فاقد الموسوي  محرم الحرام 1446 هـ": {
        "message_id": 326
    },
    "عندي فتيان اربعة  الرادود باسم الكربلائى": {
        "message_id": 327
    },
    "طايح بين خياله  مسلم الوائلي  رابطة اصحاب الكساء  1443هـ": {
        "message_id": 328
    },
    "واويلاه يم الخدر  الرادود حيدر البياتي  بحضور الملا باسم الكرب": {
        "message_id": 329
    },
    "اقطع الكلام  الرادود باسم الكربلائي": {
        "message_id": 330
    },
    "برز القمر  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء الناصرية": {
        "message_id": 331
    },
    "بندرية هلا بحسين الثاني  الرادود خضر عباس": {
        "message_id": 332
    },
    "وصية الاب  مسلم الوائلي  1446هـ": {
        "message_id": 334
    },
    "ديوانك حلم كل عاشگ  ملاعلي الوائلي وملا مسلم الوائلي مضيف سلطا": {
        "message_id": 335
    },
    "هالله هالله حسين وينه  الرادود خضر عباس": {
        "message_id": 336
    },
    "مسا الخير  الرادود باسم الكربلائي": {
        "message_id": 337
    },
    "يريح الهاب الحاج باسم الكربلائي": {
        "message_id": 338
    },
    "لو حي النبي  الرادود باسم الكربلائي": {
        "message_id": 339
    },
    "لا تسافر روحي عندك _ استديو  باسم الكربلائي": {
        "message_id": 340
    },
    "يسجلني": {
        "message_id": 341
    },
    "خلي عيونج بعيني  الحاج باسم الكربلائي": {
        "message_id": 342
    },
    "عتاب الموت - باسم الكربلائي  مونتاج كامل foul hd  ذكرى وفاة ال": {
        "message_id": 343
    },
    "للعباس اجت زينب باسم الكربلائي اصدار وحي القوافي النسخة الاصلية": {
        "message_id": 344
    },
    "باسم الكربلائي  عطر يوسف 2015": {
        "message_id": 345
    },
    "باسم الكربلائي  امك فاطمة يحسين": {
        "message_id": 346
    },
    "اجانه الصبح  الرادود باسم الكربلائي": {
        "message_id": 347
    },
    "عين الله ترعاكم - الحاج باسم الكربلائي": {
        "message_id": 348
    },
    "سبحانه سواها  الرادود حسين الزغير الكربلائي": {
        "message_id": 349
    },
    "حسين قتيل  الحاج باسم الكربلائي": {
        "message_id": 350
    },
    "جائنا الظلام": {
        "message_id": 351
    },
    "يا محلى الوداع  الرادود باسم الكربلائي": {
        "message_id": 375
    },
    "ان جان هاذي كربلاء وين شيال العلم  علاء الغريباوي": {
        "message_id": 353
    },
    "اعظم عريسين - علي بوحمد": {
        "message_id": 354
    },
    "طبعي كربلائي باسم الكربلائي # حطوا لايك ونزلو على الوصف مهم ": {
        "message_id": 355
    },
    "عاشور هل هلاله  الرادود باسم الكربلائي": {
        "message_id": 356
    },
    "يا ال هاشم - الرادود  قحطان البديري - الشاعر  عقيل الشيباني": {
        "message_id": 357
    },
    "ملكني  - جمال عيونه لوحه - حسين الحب الاول - كالو…": {
        "message_id": 358
    },
    "شيخ الانصار  الرادود حسين والي اللامي": {
        "message_id": 359
    },
    "اعصار  ملا محمد بوجبارة  ليلة 6 محرم 1445  ماتم النمر": {
        "message_id": 360
    },
    "وجه الصباح محمد باقر الخاقانيالذاكر سيد سجاد الخرسانيمضيف…": {
        "message_id": 361
    },
    "الخيال الشيعي  لؤي البغدادي - شاعر ال الصدر - عباس عبد الحسن ": {
        "message_id": 362
    },
    "الوعد الصادق  حصريا 2024": {
        "message_id": 363
    },
    "انشودة عهد النجباء": {
        "message_id": 364
    },
    "دهد يا عون  ملا عباس العقابي": {
        "message_id": 366
    },
    "الهيبة اوبريت  فتية الكميل": {
        "message_id": 367
    },
    "علي الدلفي وسيد فاقد الموسوي - فرحة حيدرية #عيد_الغدير": {
        "message_id": 368
    },
    "فرحة غديرك  فتية الكميل": {
        "message_id": 369
    },
    "امام النحل (حصرياً) 2015  mustafa al rubaie - i": {
        "message_id": 370
    },
    "من المتمسكين - علي بوحمد  min al-mutamasakeen - ali bouhamad": {
        "message_id": 371
    },
    "عطلتنه رسمية - حسين البغدادي - علي زوره - فواد الفرطوسي - علي ال": {
        "message_id": 372
    },
    "اخيتكم في الله  محمود اسيري - محمد الخياط - علي بوحمد - محمد بو": {
        "message_id": 373
    },
    "كلما اسهر الليل  الرادود باسم الكربلائي": {
        "message_id": 374
    },
    "واقع لو حلم - dream or reality  الملا محمد بوجبارة - الميرزا محمد…": {
        "message_id": 376
    },
    "اهز مهدك  الرادود باسم الكربلائي": {
        "message_id": 377
    },
    "قيامة العباس  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء الناص": {
        "message_id": 380
    },
    "محرم الذهب - ملا مصطفى السوداني - الكوفة- حي ميسان": {
        "message_id": 381
    },
    "علكو الرايات": {
        "message_id": 383
    },
    "مرتضى حرب ll زلم النيبه ll محرم 1441 هجري": {
        "message_id": 384
    },
    "ويلي يالاكبر حاجيني باسم كربلائي": {
        "message_id": 385
    },
    "حلو بيارغهم  محرم  1440 هجري 2018 م": {
        "message_id": 386
    },
    "انا دامي محرم 1441 هجري": {
        "message_id": 388
    },
    "اذان العشق  سيد سلام الحسيني  حسينية غريب طوس عليه السلام": {
        "message_id": 389
    },
    "يا فاطمة قومي الى الطفوف": {
        "message_id": 392
    },
    "سيوف اهلك مالاكوها-جبار الحريشاوي -هوسات -الطف يازلمه يعارك بيه ": {
        "message_id": 393
    },
    "هل يوم نعزي فاطمه  ملا مجتبى الكعبي  قافله احزان الرباب  م": {
        "message_id": 394
    },
    "حطيتلك عله بدليلي  سيد فاقد الموسوي": {
        "message_id": 395
    },
    "يالماشي لبعيد  جديد2025": {
        "message_id": 396
    },
    "انا ام الرواي  الحاج باسم الكربلائي": {
        "message_id": 397
    },
    "مقتل الحسين  الرادود ميرزا حيدر الابراهيمي - حسينية عزاء الناصرية…": {
        "message_id": 398
    },
    "اهات الحسين  الميرزا حيدر الابراهيمي - محرم ١٤٤٧ هـ": {
        "message_id": 399
    },
    "مسلم وسبع الكنطرة  محمد عامر الاسدي  حسينية جنة الزهراء  محرم": {
        "message_id": 400
    },
    "ابطال هجت  سيد فاقد الموسوي  محرم الحرام  1447هـ": {
        "message_id": 401
    },
    "اوتار التكبير  الحاج باسم الكربلائي": {
        "message_id": 402
    },
    "اويلي حسين طايح  حيدر البياتي  لطميات محرم 1447 هـ": {
        "message_id": 403
    },
    "قصة حزن  الحاج باسم الكربلائي": {
        "message_id": 404
    },
    "ما تذل شيعة علي - جبار الحريشاوي - #محرم  1447 هــ": {
        "message_id": 405
    },
    "گلبك مكاني  الحاج باسم الكربلائي": {
        "message_id": 406
    },
    "بسملة الطف  حيدر البياتي  لطميات محرم 1447 هـ": {
        "message_id": 407
    },
    "جمال الله  حيدر البياتي  لطميات محرم 1447 هـ": {
        "message_id": 408
    },
    "طال انتظاري  الشيخ حسين الاكرف": {
        "message_id": 409
    },
    "اجمل علاقة  كرار الكربلائي محرم الحرام 1447 هـ  #جديد2025 راح…": {
        "message_id": 410
    },
    "سمعي يمي فاطمة  احمد الباوي 1446 هـ": {
        "message_id": 411
    },
    "مسلم الكوفه  رضا الاراكي reza al - araki  مضيف سلطان بني هاشم…": {
        "message_id": 422
    },
    "ها يخيمتنه  الحاج باسم الكربلائي": {
        "message_id": 413
    },
    "رف ياعلم  الملا محمد باقر الخاقاني هيئة الحسن المحتبى عليه ا": {
        "message_id": 414
    },
    "ماحسبت هالكثر  الحاج باسم الكربلائي": {
        "message_id": 415
    },
    "سلوان الناصري   ها يسبع الكنطرة   youtube": {
        "message_id": 416
    },
    "جاء الاربعين  محمد الجنامي  المشاية 1445 هـ 2023 م": {
        "message_id": 417
    },
    "هاي الدنية  الرادود باسم الكربلائي": {
        "message_id": 418
    },
    "الحك يعباس  الرادود الحاج حيدر السعد  محرّم الحرام 1447 هـ - 2": {
        "message_id": 419
    },
    "عباس الحك  سيد فاقد الموسوي  محرم الحرام  1447هـ": {
        "message_id": 420
    },
    "من هنا كربلاء  سيد فاقد الموسوي  مشاية الاربعين  2025": {
        "message_id": 421
    },
    "ايها الصاحب العَجل  الحاج باسم الكربلائي": {
        "message_id": 423
    },
    "قسما  الشيخ حسين الاكرف": {
        "message_id": 424
    },
    "حيدريون  الرادود سيد فاقد الموسوي  حسينية قصر الزهراء  1446هـ": {
        "message_id": 425
    },
    "طش ضعنه ll محمد الحلفي": {
        "message_id": 426
    },
    "انا الخليفة  الرادود باسم الكربلائي": {
        "message_id": 427
    },
    "اويلي من لفت ليله  محمد الجنامي  تراث المحمره": {
        "message_id": 428
    },
    "يهاجر _مونتاج_ باسم الكربلائي": {
        "message_id": 429
    },
    "شلون اصبر على الاه  باسم الكربلائي": {
        "message_id": 431
    },
    "طلع شباب من الخيم  الرادود باسم الكربلائي": {
        "message_id": 432
    },
    "هاك جروح يا مهدينه  باسم الكربلائي ": {
        "message_id": 433
    },
    "فنة يجي 4k  سيد فاقد الموسوي  بيت الاحزان  الليالي العلوية…": {
        "message_id": 434
    },
    "ماغفت عيني  الرادود باسم الكربلائي": {
        "message_id": 435
    },
    "بنات النبي  الرادود باسم الكربلائي": {
        "message_id": 436
    },
    "مهلا بنات النبي  الرادود باسم الكربلائي": {
        "message_id": 437
    },
    "يليله يرمله  الرادود باسم الكربلائي": {
        "message_id": 438
    },
    "عوف المشرعه ii  ملا علي باشا الكربلائي ii  زيارة الاربعين 14447…": {
        "message_id": 439
    },
    "وينك   الرادود باسم الكربلائي": {
        "message_id": 440
    },
    "انني عرش النحيب  الرادود باسم الكربلائي": {
        "message_id": 441
    },
    "علي يشبه علي   حيدر الفريجي #جديد2025": {
        "message_id": 442
    },
    "فزاعية شيخ القادة  ملا عباس العقابي جديد 2024 #اكسبلور #لطميات…": {
        "message_id": 443
    },
    "مو انه يا حزن  سيد سلام الحسيني  حسينية غريب طوس عليه السلام": {
        "message_id": 444
    },
    "مكطوع جف العباس": {
        "message_id": 445
    },
    "دنكت لحسين مهضومه السهام ( كامله ) احمد الساعدي ( واحسيناه وامام": {
        "message_id": 447
    },
    "مو عليله  الرادود باسم الكربلائي": {
        "message_id": 448
    },
    "حيهم صاح حيهم - حسين المرياني - محرم الحرام ١٤٤٧ هـ - هيئة لواء ": {
        "message_id": 449
    },
    "حيدريون  سيد فاقد الموسوي": {
        "message_id": 450
    },
    "لعب جوله بيوم الهد  عقيل الحريشاوي  مضيف زمن الغيبه": {
        "message_id": 451
    },
    "اذن الغضب  يحيى عفارة": {
        "message_id": 452
    },
    "يا رايه ليش الوحدج لطميات على مشايه حزينه": {
        "message_id": 453
    },
    "سلام  وعن بعد  سيد سلام الحسيني [ محرم الحرام 1446 هـ ] عزاء ال": {
        "message_id": 454
    },
    "يغادر كل ملك": {
        "message_id": 455
    },
    "لميت المواكب  سيد فاقد الموسوي  1445 هـ": {
        "message_id": 456
    },
    "قصة الاكبر  محمد باقر الخاقاني  حسينية غريب طوس عليه السلام 14": {
        "message_id": 457
    },
    "اكبري اكبري سجاد العلياويموكب شفيع المذنبيناصدار محرم ال": {
        "message_id": 458
    },
    "اولسنا على الحق - حيدر خليل  - 2024": {
        "message_id": 459
    },
    "مملوك الحسين  محمد باقر الخاقاني  حسينية غريب طوس عليه السلام": {
        "message_id": 460
    },
    "فاطمة ملجؤنا  حسين خير الدين": {
        "message_id": 473
    },
    "ياليتنا  الرادود #علي_سعيد_الوائلي  جديد #2025": {
        "message_id": 462
    },
    "شاهد الخلائق   سيد حيدر الموسوي ": {
        "message_id": 463
    },
    "مولانا ابا الفضل  حيدر الفريجي  حسينية القربان": {
        "message_id": 464
    },
    "مسلم المهيوب. محمد الفاطمي  هيئه شيخ الانصار اليالي الفاطميه": {
        "message_id": 465
    },
    "الما يعزب للضيف  الرادود حمزة الشريفي  الذاكر مسلم الحسناوي  ": {
        "message_id": 466
    },
    "ياساقي العشق  الملا رباح العيساوي - موكب نوماس الهواشم الموحد -": {
        "message_id": 467
    },
    "سيد العشق  محمود حيدر عواضة": {
        "message_id": 468
    },
    "احبك يابو فاضل  الرادود حمزة الشريفي  الذاكر علي ستار  هيئة س": {
        "message_id": 469
    },
    "توه حله  حمزه الشريفي  هيئة مجانين الحسين ع  1446هـ": {
        "message_id": 470
    },
    "لليزور حسين  باسم الكربلائي": {
        "message_id": 471
    },
    "هل ترانا - باسم الكربلائي و قحطان البديري": {
        "message_id": 472
    },
    "حيهم يجرحي": {
        "message_id": 474
    },
    "رديتلك  سيد سلام الحسيني": {
        "message_id": 475
    },
    "اية للسائلين  الملا محمد باقر الخاقاني - هيئة لواء زينب عليها السلام…": {
        "message_id": 476
    },
    "حرة نسب الرادود حيدر البياتي": {
        "message_id": 477
    },
    "جريمة قتل  الحاج باسم الكربلائي": {
        "message_id": 478
    },
    "لمحة بصر  الحاج باسم الكربلائي": {
        "message_id": 480
    },
    "مرتضى حرب  مالي ذنب  الليالي الفاطمية 1447 هجري": {
        "message_id": 481
    },
    "شيعوا نعش الطاهرة المظلومة   باسم الكربلائي   youtube": {
        "message_id": 482
    },
    "يا اسماء  الملا محمد باقر الخاقاني - الليالي الفاطمية ١٤٤٦ هـ …": {
        "message_id": 483
    },
    "زينب هالمسيه تصيح وين المرتضى وينه  باسم الكربلائي": {
        "message_id": 484
    },
    "صلت صلاة الايات  الرادود باسم الكربلائي": {
        "message_id": 485
    },
    "خجل  الحاج باسم الكربلائي": {
        "message_id": 486
    },
    "للنبي محروقه باب  الرادود باسم الكربلائي": {
        "message_id": 487
    },
    "هل انبا المسمار خير الورى  شهادة الزهراء عليها السلامالملا باسم…": {
        "message_id": 488
    },
    "قادم بثاري  الرادود باسم الكربلائي": {
        "message_id": 489
    },
    "اذكر انه  الرادود باسم الكربلائي": {
        "message_id": 490
    },
    "فارس السبع الشداد  الرادود باسم الكربلائي": {
        "message_id": 491
    },
    "سؤالي  الرادود باسم الكربلائي": {
        "message_id": 492
    },
    "ليلة وفاتي  الرادود باسم الكربلائي": {
        "message_id": 493
    },
    "دار الوكت  سيد فاقد الموسوي": {
        "message_id": 494
    },
    "فكر انته بمقتلك  الرادود باسم الكربلائي": {
        "message_id": 495
    },
    "لو فرض  الرادود باسم الكربلائي": {
        "message_id": 496
    },
    "سواد الطف  الرادود باسم الكربلائي": {
        "message_id": 497
    },
    "انا العباس ابو النوماس تعرفوني": {
        "message_id": 498
    },
    "اقوى لطمية بصوت كريم المالكي وحي الشريعه 2019بس تسمعه راح تنزله": {
        "message_id": 499
    },
    "زينب تلطم عله الراس  الرادود الحاج باسم الكربلائي": {
        "message_id": 500
    },
    "غضب رب العباد الملا باسم الكربلائي": {
        "message_id": 501
    }
}
