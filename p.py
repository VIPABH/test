from telethon import TelegramClient, events
import redis, os
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
bot = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
user_states = {}
@bot.on(events.NewMessage)
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
    key = f"رد:{text}"
    reply_value = r.get(key)
    if reply_value:
        await event.reply(reply_value)
bot.run_until_disconnected()
