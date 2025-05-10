from database import store_whisper, get_whisper #type: ignore
from playwright.async_api import async_playwright 
import asyncio, os, json, random, uuid, operator
from ABH import ABH, events #type: ignore
from telethon import Button
banned_url = [
    9,  25, 94, 131, 175,
    26, 40, 110, 136, 194,
    71, 72, 111, 142, 212,
    77, 79, 114, 148, 230,
    80, 81, 115, 150, 245,
    82, 93, 121, 152, 254,
    273, 275
]
latmiyat_range = range(50, 315)
async def send_random_latmia(event):
    try:
        chosen = random.choice(list(latmiyat_range))
        if chosen in banned_url:
            return await send_random_latmia(event)
        latmia_url = f"https://t.me/x04ou/{chosen}"
        await event.reply(file=latmia_url)
    except Exception as e:
        await event.reply(f"اعد المحاولة مره اخرى")
@ABH.on(events.NewMessage(pattern=r"^(لطمية|لطميه)$"))
async def handle_latmia_command(event):
    await send_random_latmia(event)
@ABH.on(events.NewMessage(pattern='عاشوراء'))
async def ashourau(event):
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

@ABH.on(events.NewMessage(pattern='ميم|ميمز'))
async def meme(event):
    global c
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
            except Exception as e:
                result = builder.article(
                    title='خطأ في الإرسال',
                    description="حدث خطأ أثناء معالجة طلبك.",
                    # text=f' خطأ: {str(e)}'
                )
        else:
            return
        await event.answer([result])
@ABH.on(events.CallbackQuery)
async def callback_Whisper(event):
    data = event.data.decode('utf-8')
    if data.startswith('send:'):
        whisper_id = data.split(':')[1]
        whisper = get_whisper(whisper_id)
        if whisper:
            if event.sender_id == whisper.sender_id or event.sender_id == whisper.reciver_id:
                await event.answer(f"{whisper.message}", alert=True)
            else:
                await event.answer("عزيزي الحشري، هذه الهمسة ليست موجهة إليك!", alert=True)
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
    url = event.pattern_match.group(1)
    if any(banned in url.lower() for banned in BANNED_SITES):
        await event.reply("🚫 هذا الموقع محظور!\nجرب تتواصل مع المطور @k_4x1")
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
        await event.reply("❌ فشل التقاط لقطة الشاشة، تأكد من صحة الرابط أو جرب مجددًا.")
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
async def add_to(event):
    global alert_ids
    chat = await event.get_chat()
    if chat.id not in alert_ids:
        try:
            alert_ids.add(chat.id)
            save_alerts()
            chat_name = chat.title if hasattr(chat, 'title') else chat.first_name
            return
        except Exception as e:
            await alert(f"فشل إضافة المحادثة: {chat_name} \n {chat.id} - {e} ")
@ABH.on(events.NewMessage(pattern="/alert"))
async def send_alert(event):
    if event.sender_id != K_4X1:
        return
    message_text = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        message_text = replied_msg.text
    else:
        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) > 1:
            message_text = command_parts[1]
    if not message_text:
        await event.reply("يرجى الرد على رسالة أو كتابة نص بعد `/alert`.")
        return
    await event.reply(f"🚀 جاري إرسال التنبيه إلى {len(alert_ids)} محادثة...")
    for dialog_id in alert_ids:
        try:
            await ABH.send_message(dialog_id, f"**{message_text}**")
            await alert(f"✅ تم الإرسال إلى: {dialog_id}")
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
    global l, m1, reply
    sender_id = event.sender_id
    if sender_id in l and l[sender_id]:
        await event.reply("هيييي ماتكدر تسوي همستين بوقت واحد")
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("صديقي الامر هاذ ميشتغل اذا مو رد")
        return
    whisper_id = str(uuid.uuid4())[:6]
    from_user = await event.get_sender()
    to_user = await reply.get_sender()
    whisper_links[whisper_id] = {
        "from": sender_id,
        "to": reply.sender_id,
        "chat_id": event.chat_id,
        "from_name": from_user.first_name,
        "to_name": to_user.first_name
    }
    save_whispers()
    button = Button.url("اضغط هنا للبدء", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    m1 = await event.reply(
        f'همسة مرسلة من {from_user.first_name} إلى {to_user.first_name}',
        buttons=[button]
    )
    l[sender_id] = True
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if not data:
        await event.reply("الهمسة غير موجودة في التخزين.")
        return
    if event.sender_id != data['to'] and event.sender_id != data['from']:
        await event.reply("لا يمكنك مشاهدة هذه الهمسة.")
        return
    sender = await event.get_sender()
    if 'original_msg_id' in data and 'from_user_chat_id' in data:
        await ABH.forward_messages(
            event.sender_id,
            messages=data['original_msg_id'],
            from_peer=data['from_user_chat_id']
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
    from_name = data.get("from_name", "مجهول")
    to_name = data.get("to_name", "مجهول")
    await m1.delete()
    m2 = await ABH.send_message(
        data['chat_id'],
        f'همسة مرسلة من ({from_name}) إلى ({to_name})',
        buttons=[b], reply_to=reply.id)
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
