from telethon import TelegramClient, events
from ABH import ABH
import redis, os
r = redis.Redis(host='localhost', port=6379)  # ← صحيح
user_states = {}
@ABH.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.raw_text.strip()
    if user_id in user_states:
        state = user_states[user_id]
        if state["step"] == "name":
            state["name"] = text
            state["step"] = "text"
            await event.reply("📝 أرسل الآن **كلام الرد**.")
        elif state["step"] == "text":
            reply_name = state["name"]
            reply_text = text
            key = f"رد:{reply_name}"
            r.set(key, reply_text)
            user_states.pop(user_id)
            await event.reply(f"✅ تم حفظ الرد باسم: {reply_name}")
        return
    if text.lower() == "اضف رد":
        user_states[user_id] = {"step": "name"}
        await event.reply("✏️ أرسل الآن **اسم الرد**.")
        return
    if text.lower() == "الردود":
        keys = r.keys("رد:*")
        if keys:
            names = [k.decode().split(":", 1)[1] for k in keys]
            await event.reply("📄 الردود:\n" + "\n".join(names))
        else:
            await event.reply("🚫 لا توجد ردود حالياً.")
    key = f"رد:{text}"
    reply_value = r.get(key)
    if reply_value:
        await event.reply(reply_value.decode("utf-8"))
