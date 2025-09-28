from telethon import events, Button
from ABH import ABH
import uuid
active_sessions = {}
@ABH.on(events.NewMessage(pattern="^تعيين رقم$"))
async def set_num(e):
    session_id = str(uuid.uuid4())[:6]
    active_sessions[session_id] = {"user_id": e.sender_id, "number": None}
    bot_username = (await ABH.get_me()).username
    button = Button.url(
        "اضغط لتعيين الرقم",
        url=f"https://t.me/{bot_username}?start={session_id}"
    )
    await e.reply("✅ تم فتح جلسة لتعيين الرقم.\nالرجاء الضغط على الزر أدناه.", buttons=button)
@ABH.on(events.NewMessage(pattern="^/start (.+)"))
async def receive_number(e):
    session_id = e.pattern_match.group(1)
    user_id = e.sender_id
    if session_id not in active_sessions:
        await e.reply("❌ الجلسة غير صالحة أو منتهية.")
        return
    session = active_sessions[session_id]
    if session["user_id"] != user_id:
        await e.reply("⚠️ لا يمكنك تعيين رقم في جلسة شخص آخر.")
        return
    await e.reply("📨 أرسل الرقم الذي تريد تعيينه (أرقام فقط).")
    @ABH.on(events.NewMessage(from_users=user_id))
    async def save_number(ev):
        if ev.text.startswith("/start"):
            return
        if not ev.text.isdigit() and ev.text == "/start":
            await ev.reply("❌ الرجاء إرسال رقم صالح فقط.")
            return
        session["number"] = ev.text
        await ev.reply(f"✅ تم حفظ الرقم: {ev.text}")        
        ABH.remove_event_handler(save_number, events.NewMessage)
@ABH.on(events.NewMessage)
async def guess_number(e):
    for session_id, session in active_sessions.items():
        if session["number"] and e.text == session["number"]:
            await e.reply(f"🎉 تهانينا! لقد حزرت الرقم الصحيح ({session['number']})")
            return
