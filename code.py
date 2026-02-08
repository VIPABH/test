from Resources import wfffp, username, suras, ignore_phrases, لطميات, ment, mention, to, hint
import asyncio, os, json, random, uuid, operator, requests, re, time, httpx 
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.types import DocumentAttributeVideo
from playwright.async_api import async_playwright
from database import store_whisper, get_whisper
from telethon import events, Button
from collections import Counter
from Program import chs
from ABH import ABH, r
async def creat_useFILE():
    if not os.path.exists('use.json'):
        with open('use.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
async def botuse(types):
    x = 0
    # await creat_useFILE()
    # if isinstance(types, str):
    #     types = [types]
    # with open('use.json', 'r', encoding='utf-8') as f:
    #     try:
    #         data = json.load(f)
    #     except json.JSONDecodeError:
    #         data = {}
    # for t in types:
    #     if t in data:
    #         data[t] += 1
    #     else:
    #         data[t] = 1
    # with open('use.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
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
async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False
async def otherevents(e):
    if not e.is_group:
        return
    t = e.text
    if t == 'اسمي':
        await e.reply(f'`{e.sender.first_name}`')
    elif t in ('اسمه', 'الاسم'):
        r = await e.get_reply_message()
        if not r:
            return
        await e.reply(f'`{r.sender.first_name}`')
    elif t == 'رقمي':
        s = await e.get_sender()
        p = s.phone if getattr(s,"phone",None) else None
        await e.reply(f"`+{p}` " if p else "واحد عراق")
    elif t in ('رقمة', 'رقمه'):
        r = await e.get_reply_message()
        if not r:
            return
        s = await r.get_sender()
        p = s.phone if getattr(s,"phone",None) else None
        await e.reply(f"`+{p}`" if p else "واحد عراق")
    elif t in ("يوزراتي", "يوزراته", "يوزراتة"):
        if t == 'يوزراتي':
            s = e.sender
        else:
            r = await e.get_reply_message()
            if not r:
                return
            s = await r.get_sender()
        usernames = []
        if getattr(s, "usernames", None):
            for u in s.usernames:
                if getattr(u, "username", None):
                    usernames.append(u.username)
        if getattr(s, "username", None):
            usernames.insert(0, s.username)
        usernames = list(dict.fromkeys(usernames))
        utext = "\n".join(f"@{u}" for u in usernames)
        await e.reply(
            utext if usernames else ("فقير ماعندك يوزرات NFT" if t == "يوزراتي" else "ليس لديه أي يوزرات NFT")
        )
    elif t in ("يوزري", "يوزرة"):
        u = None
        if t == "يوزري":
            u = await username(e)
        else: 
            r = await e.get_reply_message()
            if not r:
                await e.reply("يرجى الرد على رسالة المستخدم")
                return
            s = await r.get_sender()
            u = getattr(s, "username", None)
        await e.reply(f"`{u}`" if u else "لا يوجد له يوزر")
@ABH.on(events.NewMessage(pattern=r'^(قرآن|قران|القران الكريم|القرآن الكريم|سورة .+)$'))
async def quran(event):
    text = event.text
    sorah_name = event.pattern_match.group(1)
    me = await event.client.get_me()
    username = me.username
    c = f'**[Enjoy dear]**(https://t.me/{username })'
    button = [Button.url("🫀", "https://t.me/x04ou")]
    if text in ['قرآن', 'قران', 'القران الكريم', 'القرآن الكريم']:
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
        else:
            return
    if text.startswith('سورة '):
        if not sorah_name:
            return
        if sorah_name not in suras:
            return
        num = suras[sorah_name]
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
DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
DEFAULT_SYSTEM_PROMPT = (
    "اذا سألتك عن اسمك كول مخفي واذا عن المطور كول ابن هاشم"
    "واجعل الرد ب اجابات بسيطة ودقيقة")
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3.1"
async def get_deepinfra_reply(user_input):
    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                DEEPINFRA_API_URL,
                json=payload,
                headers=headers)
            if response.status_code != 200:
                return
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
      await hint(f"❌ حدث خطأ: {str(e)}\n ai")
      return 
@ABH.on(events.NewMessage(pattern=r"^مخفي\s*(.*)"))
async def bot_handler(event):
    user_q = event.pattern_match.group(1)
    x = event.text
    if (
        not user_q
        or x in ignore_phrases
        or x.startswith("مخفي اختار")
        or x.startswith("مخفي نزله")
        or x.startswith("مخفي نزلة")
    ):
        return
    if not user_q:
        return
    async with event.client.action(event.chat_id, "typing"):
        reply = await get_deepinfra_reply(user_q)
        if reply:
            await chs(event, reply)
@ABH.on(events.NewMessage(pattern='^اوامر الحظ$'))
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

    كل المقادير تنطي 250 الف عدا المقدار 64 ينطي مليون دينار
    ''')
latmiyat_range = range(50, 504)
async def send_random_latmia(event):
    chosen = random.choice(list(latmiyat_range))
    latmia_url = f"https://t.me/x04ou/{chosen}"
    msg = await ABH.get_messages('x04ou', ids=chosen)
    if not msg:
        return await send_random_latmia(event)
    Buttons = [Button.url("🫀", "https://t.me/x04ou")]
    await ABH.send_file(event.chat_id, file=latmia_url, buttons=Buttons, reply_to=event.id,)
@ABH.on(events.NewMessage(pattern=r"^(لطمية|لطميه)$"))
async def handle_latmia_command(event):
    type = "لطمية"
    await botuse(type)
    await send_random_latmia(event)
async def مستمع_اللطميات(e):
    text = e.text.strip()
    if text not in لطميات:
        return
    msg_id = لطميات[text]["message_id"]
    b = Button.url('❤', url=f'https://t.me/x04ou/{msg_id}')
    msgs = await ABH.get_messages('x04ou', ids=[msg_id])
    if not msgs:
        return
    msg = msgs[0]
    await ABH.send_file(e.chat_id, msg, reply_to=e.id, buttons=b)
button = [Button.inline('التالي', data=f'next'), Button.inline('السابق', data=f'retrunback')]
ITEMS_PER_PAGE = 50
pages_db = {}
async def render_page(chat_id, user_id, page_number):
    start = page_number * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    buttons = [
        [
            Button.inline("◀️ السابق", data=f"back:{page_number}"),
            Button.inline("▶️ التالي", data=f"next:{page_number}")
        ]
    ]
    msg = ""
    page_items = list(لطميات.items())[start:end]
    for idx, (name, _) in enumerate(page_items, start=1):
        msg += f"{idx} - ( `{name}` )\n"
    msg_id = pages_db[chat_id][user_id]["msg_id"]
    new_text = f'{msg}\n                         القائمة ( 7/{pages_db[chat_id][user_id]["page"]} )'
    await ABH.edit_message(chat_id, msg_id, new_text, buttons=buttons)
    pages_db[chat_id][user_id]["page"] = page_number
@ABH.on(events.NewMessage(pattern='^لطميات$'))
async def listlatmeat(e):
    chat_id = e.chat_id
    user_id = e.sender_id
    msg = await e.reply("[حافر](https://t.me/x04ou)")
    if chat_id not in pages_db:
        pages_db[chat_id] = {}
    pages_db[chat_id][user_id] = {
        "page": 1,
        "msg_id": msg.id
    }
    await render_page(chat_id, user_id, 1)
async def callbacklet(e):
    chat_id = e.chat_id
    user_id = e.sender_id
    data = e.data.decode("utf-8")
    if chat_id not in pages_db or user_id not in pages_db[chat_id]:
        return
    if ":" not in data:
        return
    parts = data.split(":")
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return
    current = int(parts[1])
    if not current:
        return
    if data.startswith("next:"):
        if current == 8:
            await e.answer('انتهت القصايد المخزنه')
            return
        await render_page(chat_id, user_id, current + 1)
    elif data.startswith("back:"):
        if current == 1:
           await e.answer('انت ب اول صفحة')
           return
        await render_page(chat_id, user_id, current - 1)
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
    url = f"https://t.me/memeabh/{rl}"
    cap = random.choice(c)
    await ABH.send_file(event.chat_id, url, caption=f"{cap}", reply_to=event.id)
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
            await asyncio.sleep(1)
            screenshot_path = f"screenshot_{device}.png"
            await page.screenshot(path=screenshot_path)
        except Exception:
            screenshot_path = None
        finally:
            await browser.close()
    return screenshot_path
@ABH.on(events.NewMessage(pattern=r'كشف رابط|سكرين(?:\s*(.*))?'))
async def screen_shot(event):
    type = "سكرين"
    await botuse(type)
    url = event.pattern_match.group(1)
    if not url:
        url = f"https://t.me/{await username(event)}"
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
        for path in screenshot_paths:
            if os.path.exists(path):
                os.remove(path)
    else:
        await event.reply("فشل التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")
REDIS_KEY = "users"
def remove_user(user_id: int):
    r.srem(REDIS_KEY, user_id)
def get_all_users():
    return [int(uid) for uid in r.smembers(REDIS_KEY)]
async def add_toalert(event):
    await مستمع_اللطميات(event)                
    uid = event.chat_id if event.is_group else event.sender_id if event.is_private else None        
    if uid:
        is_new = r.sadd(REDIS_KEY, uid)                        
        if is_new:
            if event.is_private:
                user_mention = await mention(event)
                info_text = f"👤 **مستخدم جديد:**\n- الاسم: {user_mention}\n- الآيدي: `{uid}`"
            else:
                chat = await event.get_chat()
                title = getattr(chat, 'title', 'مجموعة غير معروفة')
                info_text = f"👥 **مجموعة جديدة:**\n- الاسم: {title}\n- الآيدي: `{uid}`"                        
@ABH.on(events.NewMessage(pattern="احصاء", from_users=[wfffp]))
async def show_stats(event):
    count = r.scard(REDIS_KEY)
    await event.reply(f"📊 عدد المشتركين الكلي في القاعدة: {count}")
@ABH.on(events.NewMessage(pattern=r"^نشر(?: الكروبات)?$", from_users=[wfffp]))
async def forward_messages_handler(event):
    if not event.reply_to_msg_id:
        await event.reply("❌ يرجى الرد على الرسالة التي تريد إعادة توجيهها.")
        return
    replied_msg = await event.get_reply_message()
    to_groups = "الكروبات" in event.raw_text    
    all_users = get_all_users()    
    targets = [i for i in all_users if str(i).startswith("-100")] if to_groups else all_users
    if not targets:
        await event.reply("⚠️ لا يوجد مشتركين للنشر إليهم.")
        return
    await event.reply(f"🚀 بدأ النشر إلى {len(targets)} محادثة...")
    success = 0
    failed = 0
    group_info = []    
    for dialog_id in targets:
        try:
            await ABH.forward_messages(dialog_id, replied_msg)
            success += 1
            if to_groups:
                try:
                    chat = await ABH.get_entity(dialog_id)
                    name = getattr(chat, "title", "مجموعة")
                    group_info.append(f"- {name} (`{dialog_id}`)")
                except:
                    group_info.append(f"- مجموعة (`{dialog_id}`)")
        except Exception as e:
            error_text = str(e).lower()
            if any(k in error_text for k in ["user is blocked", "chat write forbidden", "peer id invalid"]):
                remove_user(dialog_id)
            failed += 1       
    await event.reply(
        f"📢 **تقرير النشر النهائي:**\n"
        f"✅ نجاح: {success}\n"
        f"🚫 فشل: {failed}"
    )        
    if to_groups and group_info:
        report_text = "📋 **المجموعات التي استلمت النشر:**\n\n" + "\n".join(group_info)
        await ABH.send_message(wfffp, report_text)
whispers_file = 'whispers.json'
if os.path.exists(whispers_file):
    try:
        with open(whispers_file, 'r', encoding='utf-8') as f:
            whisper_links = json.load(f)
    except json.JSONDecodeError:
        whisper_links = {}
else:
    whisper_links = {}
def save_whispers():
    with open(whispers_file, 'w', encoding='utf-8') as f:
        json.dump(whisper_links, f, ensure_ascii=False, indent=2)
user_sessions = {}
l = {}
@ABH.on(events.NewMessage(pattern=r'اهمس(?:\s+(.*))?'))
async def handle_whisper(event):
    lock_key = f"lock:{event.chat_id}:همسة"
    if r.get(lock_key) != "True":
        await chs(event, 'اوامر الهمسة معطلة💔')
        return
    sender_id = event.sender_id
    target = await to(event)
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    if not target:
        await event.reply("حاول تشغل الامر اما بالرد او باليوزر او المنشن")
        return
    if getattr(target, "bot", False):
        await chs(event, 'عزيزي تسوي همسه ل بوت انت شكد حديقه')
        return
    if target_id == sender_id:
        await event.reply("شني خالي تسوي همسه لنفسك")
        return
    anymous = await ABH.get_me()
    if target_id == anymous.id:
        await event.reply("تسويلي همسه 😁؟")
        return
    ment1 = await mention(event)
    ment2 = await ment(target)
    if sender_id in l and l[sender_id]:
        whisper_id = user_sessions[event.sender_id]
        button = [
            Button.url("اكمال الهمسة", url=f"https://t.me/{anymous.username}?start={whisper_id}"), 
            Button.inline("حذف الهمسة", data=f'del_l:{sender_id}')
                  ]
        await event.reply(
            "هيييي ماتكدر تسوي همستين بوقت واحد \n **اختر احد الازرار🙂**",
        buttons=[button]
        )
        return
    whisper_id = str(uuid.uuid4())[:6]
    user_sessions[event.sender_id] = whisper_id
    button = Button.url("اضغط هنا للبدء", url=f"https://t.me/{anymous.username}?start={whisper_id}")
    m1 = await event.reply(
        f'همسة جارية الانشاء من ( {ment1} ) إلى ( {ment2} ) 🙂🙂',
        buttons=[button]
    )
    whisper_links[whisper_id] = {
        'sender_mention': ment1,
        'reciver_mention': ment2,
        'editmsg_id': m1.id,
        'chat_id': event.chat_id,
        'from': sender_id,
        'to': target_id,
        'sm': event.id,
        'done': False,
    }
    save_whispers()
    l[sender_id] = True
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if not data:
        return
    sender_id = event.sender_id
    if sender_id not in (data['from'], data['to']):
        await event.reply("لا يمكنك مشاهدة هذه الهمسة.")
        return
    if sender_id == data['to']:
        fb = [
            Button.inline(
                'حذف الهمسة',
                data=f"del_l:{data['from']}"
            ),
            Button.url(
                "رؤية الهمسة",
                url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}"
            )
        ]
        try:
            await ABH.edit_message(
                data['chat_id'],
                data['editmsg_id'],
                text=(
                    f"همسة مرسلة من ({data['sender_mention']}) "
                    f"إلى ({data['reciver_mention']}) 🙂"
                ),
                buttons=fb
            )
        except Exception:
            pass
    await botuse("مشاهدة الهمسة")
    if not (
        ('original_msg_id' in data and 'from_user_chat_id' in data)
        or 'text' in data
    ):
        await event.reply(
            f"أهلاً {await mention(event)}، ارسل نص الهمسة أو ميديا."
        )
        return
    if 'original_msg_id' in data and 'from_user_chat_id' in data:
        originals = await ABH.get_messages(
            data['from_user_chat_id'],
            ids=data['original_msg_id']
        )
        for original in originals:
            if original.media:
                video_duration = data.get('video_duration')
                try:
                    await ABH.send_file(
                        sender_id,
                        file=original,
                        caption=original.message or None,
                        reply_to=event.id,
                        ttl=int(video_duration) if video_duration else None
                    )
                except Exception:
                    await ABH.send_file(
                        sender_id,
                        file=original,
                        caption=original.message or None,
                        reply_to=event.id
                    )
            elif original.text:
                await ABH.send_message(sender_id, original.text)
    elif 'text' in data:
        await event.reply(data['text'])
@ABH.on(events.CallbackQuery(pattern=b'^del_l:(\\d+)$'))
async def delete_whisper_callback(e):
    data = e.data.decode('utf-8')
    id = int(data.replace('del_l:', ''))
    sender_id = e.sender_id
    if id != sender_id:
        await e.answer('🙄')
        return
    if sender_id in l:
        l[sender_id] = False
        b = Button.url("كيف اهمس", url=f"https://t.me/{(await ABH.get_me()).username}?start=how_can_i_whisper")
        await e.edit('تم حذف جلسة الهمسة', buttons=b)
processed_groups = set()
async def forward_whisper(event):
    if not event.is_private or (event.text and event.text.startswith('/')):
        return
    if event.text.startswith("اهمس"):
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
    b = Button.url("فتح الهمسة", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    msg = event.message
    is_photo = getattr(msg.media, 'photo', None)
    is_video = False
    video_duration = None
    if getattr(msg, "voice", None) or (msg.document and msg.document.mime_type == "audio/ogg"):
        video_duration = None
    if msg.media and (is_photo or getattr(msg.media, 'document', None) or getattr(msg, "voice", None)):
        if is_photo:
            video_duration = 30
        elif getattr(msg.media, 'document', None):
            for attr in msg.media.document.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    video_duration = attr.duration
                    is_video = True
                    break
            if not is_video and not (msg.document and msg.document.mime_type == "audio/ogg"):
                return
        whisper_links.setdefault(whisper_id, {})
        whisper_links[whisper_id]['video_duration'] = video_duration
        whisper_links[whisper_id].setdefault('original_msg_id', [])
        whisper_links[whisper_id]['original_msg_id'].append(msg.id)
        whisper_links[whisper_id]['from_user_chat_id'] = sender_id
        if not ('done' in whisper_links[whisper_id]):
            whisper_links[whisper_id]['done'] = True
        t = "تم إرسال همسة ميديا بنجاح."
    elif msg.text:
        whisper_links[whisper_id]['text'] = msg.text
        if not ('done' in whisper_links[whisper_id]):
            whisper_links[whisper_id]['done'] = True
        t = "تم إرسال همسة بنجاح."
    save_whispers()
    l[sender_id] = False
    gid = getattr(msg, 'grouped_id', None)
    if msg.media and gid:
        if gid in processed_groups:
            return
        processed_groups.add(gid)
    msg = await ABH.edit_message(
        data['chat_id'],
        data['editmsg_id'], 
        text=f'همسة مرسلة من ({data["sender_mention"]} ) إلى ( {data["reciver_mention"]} ) 🙂🙂',
        buttons=[b]
    )
    await event.reply(str(t))
    await ABH.send_message(data['chat_id'], f'هَمستك عزيزي (  {data["reciver_mention"]} )', reply_to=msg.id)
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
@ABH.on(events.NewMessage(pattern=r'^همساتي|همسات[هة]?(?:\s+|@)?(\d+|@\w+)?$'))
async def countwhispers(e):
    t = e.text
    if t == 'همساتي':
        user_id = e.sender_id
    else:
        target = await to(e)
        if not target:
            await e.reply('🙄')
            return
        user_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    file_path = 'whispers.json'
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sent_count = sum(1 for record in data.values() if record.get("from") == user_id)
    received_count = sum(1 for record in data.values() if record.get("to") == user_id)
    all = sent_count + received_count
    if all == 0:
        await chs(e, 'ما هامس ابدا')
        return
    await chs(e, f"الهمسات المرسلة والمستقبلة: {all}\n"
                  f"عدد الهمسات المرسلة: {sent_count}\n"
                  f"عدد الهمسات المستقبلة: {received_count}")
