from telethon import events, Button
from ABH import ABH
import uuid
active_sessions = {}
@ABH.on(events.NewMessage(pattern="^تعيين رقم$"))
async def set_num(e):
    if not e.is_group:
        return
    bot_username = (await ABH.get_me()).username
    button = Button.url(
        "اضغط لتعيين الرقم",
        url=f"https://t.me/{bot_username}?start={session_id}"
    )
    x = await e.reply("تم فتح جلسة لتعيين الرقم، اضغط على الزر لإرسال الرقم بالخاص", buttons=button)
    session_id = str(uuid.uuid4())[:6]
    active_sessions[session_id] = {"group_id": e.chat_id, "user_id": e.sender_id, "msgid": x, "number": None}
@ABH.on(events.NewMessage(pattern="^/start (.+)"))
async def receive_number(e):
    session_id = e.pattern_match.group(1)
    user_id = e.sender_id
    if session_id not in active_sessions:
        await e.reply("عذراً، الجلسة انتهت أو غير موجودة.")
        return
    session = active_sessions[session_id]
    if session["user_id"] != user_id:
        await e.reply("هذا الرقم ليس لك، لا يمكنك تعيينه.")
        return
    if session["number"] is not None:
        await e.reply("❌ الرقم تم تعيينه مسبقًا، لا يمكن تغييره.")
        return
    await e.reply("أرسل الرقم المميز الآن:")
    @ABH.on(events.NewMessage(from_users=user_id))
    async def save_number(ev):
        if ev.text.startswith("/start"):
            return
        if not ev.text.isdigit():
            await ev.reply("❌ الرجاء إرسال رقم صالح فقط.")
            return
        session["number"] = ev.text
        await ev.reply(f"✅ تم حفظ الرقم: {ev.text}")
        x = session["msgid"]
        await x.edit('تم تعيين الرقم ')
        ABH.remove_event_handler(save_number, events.NewMessage)
@ABH.on(events.NewMessage)
async def guess_number(e):
    if not e.is_group:
        return
    for session_id, session in active_sessions.items():
        if session["group_id"] == e.chat_id and session["number"] == e.text:
            await e.reply(f"🎉 تهانينا! لقد حزرت الرقم الصحيح ({session['number']})")
            active_sessions.pop(session_id)
            return
