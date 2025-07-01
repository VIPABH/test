from telethon.tl.types import ChannelParticipantCreator
import asyncio, os, json, random, uuid, operator, requests, re
from telethon.tl.functions.channels import GetParticipantRequest
from Resources import suras, mention, ment, wfffp, hint
from playwright.async_api import async_playwright
from database import store_whisper, get_whisper
from telethon import events, Button
from Program import CHANNEL_KEY 
from ABH import ABH
async def creat_useFILE():
    if not os.path.exists('use.json'):
        with open('use.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
async def botuse(types):
    await creat_useFILE()
    if isinstance(types, str):
        types = [types]
    with open('use.json', 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    for t in types:
        if t in data:
            data[t] += 1
        else:
            data[t] = 1
    with open('use.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
@ABH.on(events.NewMessage(pattern='^رسائل المجموعة$'))
async def eventid(event):
    if not event.is_group:
        return
    x = event.id
    await event.reply(f"`{x}`")
@ABH.on(events.NewMessage(pattern=r"زر\s+(.+)"))
async def handler(event):
    if not event.is_group:
        return
    type = "زر"
    await botuse(type)
    if not event.is_reply:
        return await event.reply("يجب الرد على رسالة تحتوي على كابشن.")
    reply_msg = await event.get_reply_message()
    caption = reply_msg.text or getattr(reply_msg, 'message', None)
    if not caption:
        return await event.reply("الرسالة التي رددت عليها لا تحتوي على كابشن نصي.")
    full_text = event.pattern_match.group(1).strip()
    items = [item.strip() for item in full_text.split("|") if "\\" in item]
    if not items:
        return await event.reply("تأكد من كتابة الأزرار بصيغة: `اسم الزر \\ الرابط`")
    buttons, row = [], []
    for item in items:
        try:
            label, url = map(str.strip, item.split("\\", 1))
            row.append(Button.url(label, url))
        except Exception as e:
            await ABH.send_message(wfffp, f'حدث خطأ في الازرار {e}')
            continue
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await event.respond(message=caption, buttons=buttons)
@ABH.on(events.NewMessage(pattern="^كشف همسة|كشف همسه$"))
async def whisper_scanmeme(event):
    if not event.is_group:
        return
    type = "كشف همسة"
    await botuse(type)
    r = await event.get_reply_message()
    if not r:
        await event.reply("لازم تسوي رد على همسة للكشف😎")
        return
    if r.text and ("همسة" in r.text or "همسه" in r.text):
        x = random.choice([
            "اييييع",
            "عيني السكرينات عندي موجودة \n اي شيء يصير ادزهن",
            "مامي 😭",
            "بموووووت 😭",
            "المشرفين كلهم فيمبوي والله وكلهم مقدمين تنازلات",
            "كليلي ميو علمود ارفعج😭",
            "😭 😭 😭 😭"
            "🍌🍌",
            "🤤",
            "😋😋😋😋",
            "دروح لا اكفر بربك",
            "حزبي الله",
            "البتك مالي",
            "طيب وش بسوي؟",
            "تره حته المالك!"
    ])
        await event.reply(f"الهمسة 👇\n \n **{x}**")
    else: 
        await event.reply("ماكدرت اكشفها💔")
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
async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False
@ABH.on(events.NewMessage(pattern=r'^رفع معاون$'))
async def add_assistant(event):
    if not event.is_group:
        return
    type = "رفع معاون"
    await botuse(type)
    sm = await mention(event)
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    if not (await is_owner(event.chat_id, user_id) or user_id == 1910015590):
        return await event.reply(f"عذراً {sm}، هذا الأمر مخصص للمالك فقط.")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply(f"عزيزي {sm}، يجب الرد على رسالة المستخدم الذي تريد إضافته.")
    target_id = reply.sender_id
    data = load_auth()
    if chat_id not in data:
        data[chat_id] = []
    if target_id not in data[chat_id]:
        data[chat_id].append(target_id)
        save_auth(data)
        sender = await reply.get_sender()
        rm = await ment(sender)
        await event.reply(f"تم رفع المستخدم {rm} إلى معاون في هذه المجموعة.")
    else:
        await event.reply(f"المستخدم {rm} موجود مسبقًا في قائمة المعاونين لهذه المجموعة.")
@ABH.on(events.NewMessage(pattern=r'^تنزيل معاون$'))
async def remove_assistant(event):
    if not event.is_group:
        return
    type = "تنزيل معاون"
    await botuse(type)
    sm = await mention(event)
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    if not (await is_owner(event.chat_id, user_id) or user_id == 1910015590):
        return await event.reply(f"عذرًا {sm}، هذا الأمر مخصص للمالك فقط.")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply(f"عزيزي {sm}، يجب الرد على رسالة المستخدم الذي تريد تنزيله.")
    target_id = reply.sender_id
    data = load_auth()
    e = await reply.get_sender()
    rm = await ment(e)
    if chat_id in data and target_id in data[chat_id]:
        data[chat_id].remove(target_id)
        save_auth(data)
        await event.reply(f"تم إزالة {rm} من قائمة المعاونين لهذه المجموعة.")
    else:
        await event.reply(f"{rm} غير موجود في قائمة المعاونين لهذه المجموعة.")
async def m(user_id):
    try:
        user = await ABH.get_entity(user_id)
        name = getattr(user, 'first_name', None) or 'غير معروف'
        return f"[{name}](tg://user?id={user.id})"
    except:
        return f"`{user_id}`"
@ABH.on(events.NewMessage(pattern='^المعاونين$'))
async def show_assistants(event):
    type = "المعاونين"
    await botuse(type)
    if not event.is_group:
        return
    chat_id = str(event.chat_id)
    data = load_auth()
    msg = ''
    if chat_id in data and data[chat_id]:
        msg = "📋 **قائمة المعاونين في هذه المجموعة**\n\n"
        for idx, user_id in enumerate(data[chat_id], start=1):
            mention_text = await m(user_id)
            msg += f"{idx:<2} - {mention_text:<30} \n `{user_id}`\n"
    else:
        msg += " لا يوجد معاونين حالياً في هذه المجموعة.\n"
    await event.reply(msg, parse_mode="md")
@ABH.on(events.NewMessage(pattern="^اسمي$"))
async def myname(event):
    type = "اسمي"
    await botuse(type)
    name = await mention(event)
    await event.reply(name)
@ABH.on(events.NewMessage(pattern="^اسمه|اسمة$"))
async def hisname(event):
    type = "اسمه"
    await botuse(type)
    r = await event.get_reply_message()
    if not r:
        await event.reply("يجب الرد على رسالة المستخدم")
        return
    s = await r.get_sender()
    name = await ment(s)
    await event.reply(name)
@ABH.on(events.NewMessage(pattern="^رقمي$"))
async def num(event):
 s=await event.get_sender()
 p=s.phone if getattr(s,"phone",None) else None
 await event.reply(f"`+{p}` +{p} " if p else "رقمك غير متاح")
 type = "رقمي"
 await botuse(type)
@ABH.on(events.NewMessage(pattern="^رقمة|رقمه$"))
async def hisnum(event):
 r=await event.get_reply_message()
 if not r:
  await event.reply("يجب الرد على رسالة المستخدم")
  return
 s=await r.get_sender()
 p=s.phone if getattr(s,"phone",None) else None
 await event.reply(f"`+{p}` +{p} " if p else "رقمه غير متاح")
 type = "رقمه"
 await botuse(type)
@ABH.on(events.NewMessage(pattern="^يوزراتي$"))
async def uss(event):
 s=await event.get_sender()
 type = "يوزراتي"
 await botuse(type)
 usernames=[x.username for x in s.usernames] if getattr(s,"usernames",None) else []
 if s.username: usernames.insert(0, s.username)
 usernames=list(dict.fromkeys(usernames))
 utext="\n".join(f"@{u}" for u in usernames)
 await event.reply(utext if usernames else "ليس لديك أي يوزرات NFT")
@ABH.on(events.NewMessage(pattern="^يوزراته$"))
async def hisuss(event):
 r=await event.get_reply_message()
 if not r:
  await event.reply("يجب الرد على رسالة المستخدم")
  return
 s=await r.get_sender()
 usernames=[x.username for x in s.usernames] if getattr(s,"usernames",None) else []
 if s.username: usernames.insert(0, s.username)
 usernames=list(dict.fromkeys(usernames))
 utext="\n".join(f"@{u}" for u in usernames)
 await event.reply(utext if usernames else "ليس لديه أي يوزرات NFT")
 type = "يوزراته"
 await botuse(type)
@ABH.on(events.NewMessage(pattern="^يوزري$"))
async def mu(event):
 s=await event.get_sender()
 u=s.username or (list(dict.fromkeys([x.username for x in s.usernames]))[0] if getattr(s,"usernames",None) else None)
 await event.reply(f"`@{u}` @{u}" if u else "ليس لديك يوزر")
 type = "يوزري"
 await botuse(type)
@ABH.on(events.NewMessage(pattern="^يوزره|يوزرة|اليوزر$"))
async def hisu(event):
 type = "يوزره"
 await botuse(type)
 r=await event.get_reply_message()
 if not r:
  await event.reply("يجب الرد على رسالة المستخدم")
  return
 s=await r.get_sender()
 u=s.username or (list(dict.fromkeys([x.username for x in s.usernames]))[0] if getattr(s,"usernames",None) else None)
 await event.reply(f"`@{u}` @{u}" if u else "ليس لديه يوزر")
 type = "يوزره"
 await botuse(type)
@ABH.on(events.NewMessage)
async def quran(event):
    text = event.raw_text.strip()
    me = await event.client.get_me()
    username = me.username
    c = f'**[Enjoy dear]**(https://t.me/{CHANNEL_KEY })'
    button = [Button.url("🫀", "https://t.me/x04ou")]
    if text.lower() in ['قرآن', 'قران']:
        sura_number = random.randint(1, 114)
        message = await ABH.get_messages('theholyqouran', ids=sura_number + 1)
        if message and message.media:
            await ABH.send_file(
                event.chat_id,
                file=message.media,
                caption=c,
                buttons=button, 
                reply_to=event.id
            )
            type = "قران"
            await botuse(type)
        else:
            return
    for names, num in suras.items():
        if text in names:
            type = text
            await botuse(type)
            link_id = int(num) + 1
            message = await ABH.get_messages('theholyqouran', ids=link_id)
            if message and message.media:
                await ABH.send_file(
                    event.chat_id,
                    file=message.media,
                    caption=c,
                    buttons=button, 
                    reply_to=event.id
                )
            else:
                return
AI_SECRET = "AIChatPowerBrain123@2024"
def ask_ai(q):
    url = "https://powerbrainai.com/app/backend/api/api.php"
    headers = {
        "User-Agent": "Dart/3.3 (dart:io)",
        "Accept-Encoding": "gzip",
        "content-type": "application/json; charset=utf-8"
    }
    data = {
        "action": "send_message",
        "model": "gpt-4o-mini",
        "secret_token": AI_SECRET,
        "messages": [
            {"role": "system", "content": "ساعد باللهجة العراقية وكن ذكي وودود"},
            {"role": "user", "content": q}
        ]
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
    if res.status_code == 200:
        return res.json().get("data", "ماكو رد واضح من الذكاء.")
    else:
        return "صار خطأ بالسيرفر، جرب بعدين."
@ABH.on(events.NewMessage(pattern=r"^مخفي\s*(.*)"))
async def ai_handler(event):
    user_q = event.pattern_match.group(1).strip()
    x = event.text
    ignore_phrases = ["مخفي اعفطلة", "مخفي اعفطله", "مخفي قيده", "مخفي قيدة", "مخفي طكة زيج"]
    if not user_q or x in ignore_phrases:
        return
    type = "ai"
    await botuse(type)
    async with event.client.action(event.chat_id, 'typing'):
        response = await asyncio.to_thread(ask_ai, user_q)
    await event.respond(response, reply_to=event.id)
@ABH.on(events.NewMessage(pattern='اوامر الحظ'))
async def luck_list(event):
    type = "اوامر الحظ"
    await botuse(type)
    await event.reply('''
    **اوامر الحظ** كآلاتي
    `🎲` المقدار المربح = 6
    `🎯` المقدار المربح = 6
    `⚽` المقدار المربح = 5
    `🎳` المقدار المربح = 6
    `🎰` المقدار المربح = 64
    المقدار 🎰-64 يعطي من 100000 الئ 1000000 
    الباقي يعطي 999 للثروة الكلية
    ''')
banned_url = [
    71, 72, 77,
    79, 80, 81,
    82, 93, 94,
    110, 111, 114,
    115, 121, 131,
    136, 142, 148,
    150, 152, 175,
    194, 212, 230,
    245, 254, 273,
    275, 333, 362,
    363, 364, 365,
    366, 367, 368,
    369, 370, 372,
    ]
latmiyat_range = range(50, 385)
async def send_random_latmia(event):
    chosen = random.choice(list(latmiyat_range))
    if chosen in banned_url:
        return await send_random_latmia(event)
    latmia_url = f"https://t.me/x04ou/{chosen}"
    Buttons = [Button.url("🫀", "https://t.me/x04ou")]
    await ABH.send_file(event.chat_id, file=latmia_url, buttons=Buttons, reply_to=event.id,)
@ABH.on(events.NewMessage(pattern=r"^(لطمية|لطميه)$"))
async def handle_latmia_command(event):
    type = "لطمية"
    await botuse(type)
    await send_random_latmia(event)
@ABH.on(events.NewMessage(pattern='عاشوراء'))
async def ashourau(event):
    type = "عاشوراء"
    await botuse(type)
    pic = "links/abh.jpg"
    await ABH.send_file(event.chat_id, pic, caption="تقبل الله صالح الأعمال", reply_to=event.message.id)
operations = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}
@ABH.on(events.NewMessage(pattern=r'احسب (\d+)\s*([\+\-\*/÷])\s*(\d+)'))
async def calc(event):
    type = "احسب"
    await botuse(type)
    try:
        match = event.pattern_match 
        a = int(match.group(1))
        mark = match.group(2)
        b = int(match.group(3))
        if mark in operations:
            result = operations[mark](a, b)
            await event.respond(f"النتيجة `{result}`", reply_to=event.message.id)
        else:
            await event.respond("عملية غير مدعومة!", reply_to=event.message.id)
    except ZeroDivisionError:
        await event.respond("خطأ: لا يمكن القسمة على صفر!", reply_to=event.message.id)
c = [
    "ههههههه",
    "😂",
    "يسعدلي مسائك😀"]
@ABH.on(events.NewMessage(pattern='ميم|ميمز'))
async def meme(event):
    type = "ميم"
    await botuse(type)
    rl = random.randint(2, 273)
    url = f"https://t.me/IUABH/{rl}"
    cap = random.choice(c)
    await ABH.send_file(event.chat_id, url, caption=f"{cap}", reply_to=event.id)
@ABH.on(events.InlineQuery)
async def Whisper(event):
    builder = event.builder
    query = event.text
    sender = event.sender_id
    if query.strip():
        parts = query.split(' ')
        if len(parts) >= 2:
            message = ' '.join(parts[:-1])
            recipient = parts[-1]
            try:
                if recipient.isdigit():
                    reciver_id = int(recipient)
                    username = f'ID:{reciver_id}'
                else:
                    if not recipient.startswith('@'):
                        recipient = f'@{recipient}'
                    reciver = await ABH.get_entity(recipient)
                    reciver_id = reciver.id
                    username = recipient
                whisper_id = str(uuid.uuid4())
                store_whisper(whisper_id, sender, reciver_id, username, message)
                result = builder.article(
                    title='اضغط لإرسال الهمسة',
                    description=f'إرسال الرسالة إلى {username}',
                    text=f"همسة سرية إلى \n الله يثخن اللبن عمي 😌 ({username})",
                    buttons=[
                        Button.inline(
                            text='🫵🏾 اضغط لعرض الهمسة',
                            data=f'send:{whisper_id}'
                        )
                    ]
                )
            except Exception:
                return
        else:
            return
        await event.answer([result])
        type = "همسة انلاين"
        await botuse(type)
@ABH.on(events.CallbackQuery)
async def callback_Whisper(event):
    uid = event.sender_id
    data = event.data.decode('utf-8')
    if data.startswith('send:'):
        whisper_id = data.split(':')[1]
        whisper = get_whisper(whisper_id)
        if whisper and uid == whisper.sender_id or uid == whisper.reciver_id:
            await event.answer(f"{whisper.message}", alert=True)
        else:
            await event.answer("عزيزي الحشري، هذه الهمسة ليست موجهة إليك!", alert=True)
            return
        b = [Button.inline("حذف الهمسة", data=f'delete:{whisper_id}'),
            Button.inline("رؤية الهمسة", data=f'view:{whisper_id}')]
        msg = f"""
    الهمسة تم رؤيتها من ( {whisper.username} ) عزيزي المرسل هل تريد حذفها؟
    """
        if uid == whisper.reciver_id:
            await event.edit(msg, buttons=b)
        else:
            return
@ABH.on(events.CallbackQuery(data=re.compile(rb"^delete:(.+)")))
async def delete_whisper(event):
    match = re.match(rb"^delete:(.+)", event.data)
    if not match:
        await event.answer("طلب غير صالح", alert=True)
        return
    whisper_id = match.group(1).decode()
    whisper = get_whisper(whisper_id)
    uid = event.sender_id
    if uid != whisper.sender_id:
        await event.answer("لا يمكنك حذف همسة ليست لك")
        return
    x = "how_can_i_whisper"
    b = Button.url("كيف اهمس", url=f"https://t.me/{(await ABH.get_me()).username}?start={x}")
    if not whisper:
        await event.answer(" تم حذف الهمسة مسبقًا أو غير موجودة.", alert=True)
        return
    await event.edit("🗑️ تم حذف الهمسة بنجاح", buttons=b)
@ABH.on(events.CallbackQuery(data=re.compile(rb"^view:(.+)")))
async def show_whisper(event):
    match = re.match(rb"^view:(.+)", event.data)
    if not match:
        await event.answer("طلب غير صالح", alert=True)
        return
    whisper_id = match.group(1).decode()
    whisper = get_whisper(whisper_id)
    if not whisper:
        return
    uid = event.sender_id
    if uid == whisper.sender_id or uid == whisper.reciver_id:
        await event.answer(whisper.message, alert=True)
        return
BANNED_SITES = [
    "porn", "xvideos", "xnxx", "redtube", "xhamster",
    "brazzers", "youjizz", "spankbang", "erotic", "sex"
]
DEVICES = {
    "pc": {"width": 1920, "height": 1080, "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    "android": "Galaxy S5"
}
async def take_screenshot(url, device="pc"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        if device in DEVICES:
            if isinstance(DEVICES[device], str):
                device_preset = p.devices[DEVICES[device]]
                context = await browser.new_context(**device_preset)
            else:
                context = await browser.new_context(
                    user_agent=DEVICES[device]["user_agent"],
                    viewport={"width": DEVICES[device]["width"], "height": DEVICES[device]["height"]}
                )
            page = await context.new_page()
        else:
            page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            screenshot_path = f"screenshot_{device}.png"
            await page.screenshot(path=screenshot_path)
        except Exception as e:
            screenshot_path = None
        finally:
            await browser.close()
    return screenshot_path
@ABH.on(events.NewMessage(pattern=r'كشف رابط|سكرين (.+)'))
async def screen_shot(event):
    type = "سكرين"
    await botuse(type)
    url = event.pattern_match.group(1)
    if any(banned in url.lower() for banned in BANNED_SITES):
        await event.reply(" هذا الموقع محظور!\nجرب تتواصل مع المطور @k_4x1")
        return
    devices = ['pc', 'android']
    screenshot_paths = []
    for device in devices:
        screenshot_path = await take_screenshot(url, device)
        if screenshot_path:
            screenshot_paths.append(screenshot_path)
    if screenshot_paths:
        await event.reply(f"✅ تم التقاط لقطات الشاشة للأجهزة: **PC، Android**", file=screenshot_paths)
        await asyncio.sleep(60)
        await event.delete()
    else:
        await event.reply("فشل التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")
FILE = "dialogs.json"
K_4X1 = 1910015590
def load_alert():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return set(json.load(f))
    return set()
def save_alerts():
    with open(FILE, "w") as f:
        json.dump(list(alert_ids), f)
alert_ids = load_alert()
async def alert(message):
    try:
        await ABH.send_message(K_4X1, message)
    except Exception as e:
        return
@ABH.on(events.NewMessage)
async def add_toalert(event):
    uid = None
    n = None
    if event.is_group:
        uid = event.chat_id
        n = event.chat.title
    elif event.is_private:
        uid = event.sender_id
        sender = await event.get_sender()
        n = sender.first_name or "بدون اسم"
    if uid not in alert_ids:
        alert_ids.add(uid)
        save_alerts()

        await hint(f'تم تسجيل محادثه جديده `{uid}` ↽ {n}')
@ABH.on(events.NewMessage(pattern="احصاء", from_users=[wfffp]))
async def showlenalert(event):
    await event.reply(str(len(alert_ids)))
@ABH.on(events.NewMessage(pattern="/alert", from_users=[wfffp]))
async def set_alert(event):
    type = "نشر"
    await botuse(type)
    message_text = None
    media = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        message_text = replied_msg.text
        media = replied_msg.media
    else:
        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) > 1:
            message_text = command_parts[1]
        if event.media:
            media = event.media
    if not message_text and not media:
        await event.reply("يرجى الرد على رسالة تحتوي على ملف أو كتابة نص مع مرفق بعد `/alert`.")
        return
    await event.reply(f"🚀 جاري إرسال التنبيه إلى {len(alert_ids)} محادثة...")
    for dialog_id in alert_ids:
        try:
            if media:
                await ABH.send_message(dialog_id, file=media, caption=message_text or "")
            else:
                await ABH.send_message(dialog_id, f"{message_text}")
        except Exception as e:
            await alert(f"❌ فشل الإرسال إلى {dialog_id}: {e}")
    await event.reply("✅ تم إرسال التنبيه لجميع المحادثات!")
whispers_file = 'whispers.json'
sent_log_file = 'sent_whispers.json'
if os.path.exists(whispers_file):
    try:
        with open(whispers_file, 'r') as f:
            whisper_links = json.load(f)
    except json.JSONDecodeError:
        whisper_links = {}
else:
    whisper_links = {}
if os.path.exists(sent_log_file):
    try:
        with open(sent_log_file, 'r') as f:
            sent_whispers = json.load(f)
    except json.JSONDecodeError:
        sent_whispers = []
else:
    sent_whispers = []
def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f)
def save_sent_log():
    with open(sent_log_file, 'w') as f:
        json.dump(sent_whispers, f, ensure_ascii=False, indent=2)
user_sessions = {}
l = {}
@ABH.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    type = "اهمس"
    await botuse(type)
    global l, m1, reply
    sender_id = event.sender_id
    if sender_id in l and l[sender_id]:
        await event.reply(
            "هيييي ماتكدر تسوي همستين بوقت واحد \n **جرب تدز نقطة بالخاص**",
        )
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("صديقي الامر هاذ ميشتغل اذا مو رد")
        return
    if reply.sender_id == sender_id:
        await event.reply("شني خالي تسوي همسه لنفسك")
        return
    anymous = await event.client.get_me()
    if reply.sender_id == anymous.id:
        await event.reply("تسويلي همسه 😁؟")
        return
    to_user = await reply.get_sender()
    from_user = await event.get_sender()
    rid = to_user.id
    name = from_user.first_name
    to_name = to_user.first_name
    whisper_id = str(uuid.uuid4())[:6]
    whisper_links[whisper_id] = {
        "from": sender_id,
        "r": reply.id,
        "to": reply.sender_id,
        "chat_id": event.chat_id,
        "from_name": from_user.first_name,
        "to_name": to_user.first_name
    }
    save_whispers()
    button = Button.url("اضغط هنا للبدء", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    m1 = await event.reply(
        f'همسة مرسلة من ( [{name}](tg://user?id={sender_id}) ) إلى ( [{to_name}](tg://user?id={rid}) ) 🙂🙂',
        buttons=[button]
    )
    l[sender_id] = True
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if not data:
        return
    if event.sender_id != data['to'] and event.sender_id != data['from']:
        await event.reply("لا يمكنك مشاهدة هذه الهمسة.")
        return
    type = "مشاهده الهمسه"
    await botuse(type)
    sender = await event.get_sender()
    if 'original_msg_id' in data and 'from_user_chat_id' in data:
        original = await ABH.get_messages(data['from_user_chat_id'], ids=data['original_msg_id'])
        if original.text:
            await ABH.send_message(
                event.sender_id,
                message=original.text
            )
        elif original.media:
            await ABH.send_file(
                event.sender_id,
                file=original.media,
                caption=original.text if original.text else None
            )
    elif 'text' in data:
        await event.reply(data['text'])
    else:
        await event.reply(f"أهلاً {sender.first_name}، ارسل نص الهمسة أو ميديا.")
    user_sessions[event.sender_id] = whisper_id
@ABH.on(events.NewMessage(incoming=True))
async def forward_whisper(event):
    global l, m2
    if not event.is_private or (event.text and event.text.startswith('/')):
        return
    sender_id = event.sender_id
    if sender_id not in l or not l[sender_id]:
        return
    whisper_id = user_sessions.get(sender_id)
    if not whisper_id:
        return
    data = whisper_links.get(whisper_id)
    if not data:
        return
    msg = event.message
    b = Button.url("فتح الهمسة", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    uid = data.get("from", "x04ou")
    rid = data.get("to", "x04ou")
    reply = data.get("r", "None")
    from_name = data.get("from_name", "مجهول")
    to_name = data.get("to_name", "مجهول")
    await m1.delete()
    m2 = await ABH.send_message(
        data['chat_id'],
        f'همسة مرسلة من ( [{from_name}](tg://user?id={uid}) ) إلى ( [{to_name}](tg://user?id={rid}) )',
        buttons=[b], reply_to=reply)
    if msg.media:
        whisper_links[whisper_id]['original_msg_id'] = msg.id
        whisper_links[whisper_id]['from_user_chat_id'] = sender_id
    elif msg.text:
        whisper_links[whisper_id]['text'] = msg.text
    save_whispers()
    if msg.media:
        await event.reply("تم إرسال همسة ميديا بنجاح.")
    else:
        await event.reply("تم إرسال همسة بنجاح.")
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })
    save_sent_log()
    l[sender_id] = False
@ABH.on(events.NewMessage(pattern=r'^اوامري|اوامر$'))
async def start(event):
    type = "اوامري"
    await botuse(type)
    global sid
    sid = event.sender_id
    buttons = [[
        Button.url(text="صنعهُ ب حب", url="https://t.me/K_4x1"),
        Button.url(text="رابط البوت", url="https://t.me/VIPABH_BOT"),        
        ]]
    await event.respond(
        """
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
""", buttons=buttons, reply_to=event.message.id)
@ABH.on(events.NewMessage)
async def top(event):
    if event.text == "اوامر التوب":
        await event.reply('**اوامر التوب كآلاتي** \n * `توب اليومي` | `المتفاعلين` \n ل اظهار توب اكثر 10 اشخاص تفاعل \n `رسائلي` ل اظهار رسائلك من بدايه اليوم \n `رسائلة`  ل اظهار رسائل الشخص من بداية اليوم')
    elif event.text == 'اوامر التقييد':
        await event.reply('**امر التقييد كآلاتي** \n التقييد يعمل تلقائي مع البوت يعمل كلمة بذيئة او بذيئئة او بذيئ\ه \n كل انواع الكلام البذيئ ممنوع✌')
    elif event.text == 'اوامر الالعاب':
        await event.reply('**اوامر الالعاب كآلاتي** \n *امر `/num` يختار البوت رقم من 10 وانت تحزره لديك 3 محاولات \n *امر `/rings` *امر محيبس البوت يختار رقم وانت تحزره عن طريق جيب + رقم اليد ```اذا كتبت طك + رقم اليد كان فيه خاتم تخسر😁``` \n *امر `/xo` يعمل في المجموعات مع الاعبين يمكنك تحدي الاعبين بنفس التكتيك \n امر `/quist` يسأل اسئلة دينية وينتظر اجابتك ```البوت غير مناسب للبعض 😀``` \n *امر `/faster` يعمل في المجموعات وينتظر الاعبين ل اكتشاف اسرع من يكتب الكلمة التي يطلبها البوت')
    elif event.text == 'اوامر الترجمة':
        await event.reply('**اوامر الترجمة كآلاتي** \n *امر `ترجمة` \n يعمل مع الامر او بالرد ك ```ترجمة be how you are be , you are from dust```')
    elif event.text == 'اوامر الايدي':
        await event.reply('**اوامر الايدي كآلاتي** \n *امر `كشف ايدي 1910015590`\n  يعمل رابط ل حساب الايدي يمكنك من خلاله تدخل اليه')
    elif event.text == 'اوامر الكشف':
        await event.reply('**اوامر الكشف كآلاتي** \n *امر `سكرين`| `كشف رابط https://t.me/K_4x1` \n يعمل سكرين للرابط ليكشفه اذا كان ملغم ام رابط طبيعي ')
    elif event.text == 'اوامر الحسبان':
        await event.reply('**اوامر الحسبان كآلاتي** \n *امر `/dates` يحسب لك كم باقي على رجب | شعبان |رمضان | محرم او تاريخ خاص فيك')
    elif event.text == 'اوامر الميمز':
        await event.reply('**اوامر الميمز كآلاتي** \n *امر `مخفي طكة زيج` \n بالرد ليرسل بصمه زيج للرساله المردود عليها \n `هاي بعد` ارسال فيديو للتعبير عن عدم فهمك لكلام الشخص \n `ميعرف` ارسال فيديو يعبر عن فهمك لموضوع عكس الشخص المقابل \n `استرجل`')
x = "how_can_i_whisper"
@ABH.on(events.NewMessage(pattern="/start(?: (.+))?"))
async def how_to_whisper(event):
    b = [Button.url("همسة ميديا", url=f"https://t.me/{(await ABH.get_me()).username}?start=whisper_id"),
         Button.url("همسة نص", url=f"https://t.me/{(await ABH.get_me()).username}?start=whisper_media")]
    parm = event.pattern_match.group(1)
    if not parm:
        return
    if parm == x:
        url = 'https://files.catbox.moe/7lnpz4.jpg'
        c = '**اوامر الهمسة** \n همسة نص , ايدي او يوزر \n همسة ميديا او نص بالرد فقط'
        await ABH.send_file(
            event.chat_id,
            file=url,
            caption=c,
            buttons=b, 
            reply_to=event.id
    )
    elif parm == "whisper_id":
        url = 'https://t.me/recoursec/11'
        c = '😏'
        await ABH.send_file(
            event.chat_id,
            file=url,
            caption=c,
            reply_to=event.id
        )
    elif parm == "whisper_media":
        url = 'https://t.me/recoursec/12'
        c = '😏'
        await ABH.send_file(
            event.chat_id,
            file=url,
            caption=c,
            reply_to=event.id
        )
