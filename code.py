from telethon import events, Button
from Resources import *
from ABH import ABH
import uuid, json
def create(filename: str):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
        return {}
    else:
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
NUM_FILE = 'NUM.json'
def save_json(filename: str, data: dict):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
active_sessions = {}
@ABH.on(events.NewMessage(pattern="^تعيين رقم$"))
async def set_num(e):
    if not e.is_group:
        return
    create(NUM_FILE)
    bot_username = (await ABH.get_me()).username
    session_id = str(uuid.uuid4())[:6]
    button = Button.url(
        "اضغط لتعيين الرقم",
        url=f"https://t.me/{bot_username}?start={session_id}"
    )
    msg = await e.reply(
        "📌 تم فتح جلسة لتعيين الرقم.\nاضغط على الزر وأرسل الرقم في الخاص.",
        buttons=button
    )
    active_sessions[session_id] = {
        "group_id": e.chat_id,
        "user_id": e.sender_id,
        "msgid": msg,
        "number": None
    }
@ABH.on(events.NewMessage(pattern="^/start (.+)"))
async def receive_number(e):
    if not e.is_private:
        return
    session_id = e.pattern_match.group(1)
    user_id = e.sender_id
    if session_id not in active_sessions:
        await e.reply("⚠️ عذراً، الجلسة غير موجودة أو انتهت.")
        return
    session = active_sessions[session_id]
    if session["user_id"] != user_id:
        await e.reply("❌ لا يمكنك تعيين رقم لجلسة ليست لك.")
        return
    if session["number"] is not None:
        await e.reply("❌ الرقم تم تعيينه مسبقًا.")
        return
    await e.reply("📨 أرسل الرقم المميز الآن:")
    @ABH.on(events.NewMessage(from_users=user_id))
    async def save_number(ev):
        if ev.text.startswith("/start"):
            return
        if not ev.text.isdigit():
            await ev.reply("❌ الرجاء إرسال رقم صالح فقط.")
            return
        session["number"] = ev.text
        data = create(NUM_FILE)
        data[str(session["group_id"])] = session["number"]
        save_json(NUM_FILE, data)
        await ev.reply(f"✅ تم حفظ الرقم: {ev.text}")
        msg = session["msgid"]
        await msg.edit('✅ تم تعيين الرقم بنجاح', buttons=None)
        ABH.remove_event_handler(save_number, events.NewMessage)
@ABH.on(events.NewMessage)
async def guess_number(e):
    if not e.is_group:
        return
    data = create(NUM_FILE)
    group_id = str(e.chat_id)
    if group_id in data and e.text == data[group_id]:
        await e.reply(f"🎉 تهانينا! لقد خمّنت الرقم الصحيح ({data[group_id]})")
        data.pop(group_id)
        save_json(NUM_FILE, data)
