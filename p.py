import os, json
from telethon import TelegramClient, events

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('rosebot', api_id, api_hash).start(bot_token=bot_token)

DATA_FILE = "rose.json"

def load_data():
    try:
        with open(DATA_FILE) as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

rose = load_data()

def init_user(gid, uid, name):
    gid, uid = str(gid), str(uid)
    rose.setdefault(gid, {}).setdefault(uid, {"name": name, "money": 100, "roses": 0, "giver": None})

@ABH.on(events.NewMessage(pattern=r'رفع وردة\s+(\d+)'))
async def give_rose(event):
    msg = await event.get_reply_message()
    if not msg or not msg.sender: return await event.reply("❌ يجب الرد على رسالة شخص.")
    
    gid, giver, receiver = str(event.chat_id), str(event.sender_id), str(msg.sender_id)
    number, cost = int(event.pattern_match.group(1)), int(event.pattern_match.group(1)) * 2
    init_user(gid, giver, event.sender.first_name)
    init_user(gid, receiver, msg.sender.first_name)

    if rose[gid][giver]["money"] < cost:
        return await event.reply(f"❌ لا تملك فلوس كافية. تحتاج {cost} فلوس.")
    
    rose[gid][giver]["money"] -= cost
    rose[gid][receiver]["roses"] += number
    rose[gid][receiver]["giver"] = giver
    save_data(rose)
    await event.reply(f"✅ تم رفع {number} وردة لـ {rose[gid][receiver]['name']} 🌹")

@ABH.on(events.NewMessage(pattern=r'تنزيل وردة\s+(\d+)'))
async def take_rose(event):
    msg = await event.get_reply_message()
    if not msg or not msg.sender: return await event.reply("❌ يجب الرد على رسالة شخص.")
    
    gid, actor, target = str(event.chat_id), str(event.sender_id), str(msg.sender_id)
    number = int(event.pattern_match.group(1))
    init_user(gid, target, msg.sender.first_name)
    giver = rose[gid][target].get("giver")

    cost = number if actor in [target, giver] else number * 4
    if rose[gid][target]["roses"] < cost:
        return await event.reply(f"❌ لا يمكن تنزيل {cost} وردة، يملك فقط {rose[gid][target]['roses']}.")
    
    rose[gid][target]["roses"] -= cost
    save_data(rose)
    await event.reply(f"✅ تم تنزيل {cost} وردة من {rose[gid][target]['name']} 🌹")

@ABH.on(events.NewMessage(pattern='الحساب'))
async def account(event):
    gid = str(event.chat_id)
    if gid not in rose or not rose[gid]: return await event.reply("❌ لا توجد بيانات.")
    result = "\n".join([f"👤 {d['name']}: 💰{d['money']} | 🌹{d['roses']}" for d in rose[gid].values()])
    await event.reply("📊 الحسابات:\n" + result)

ABH.run_until_disconnected()
