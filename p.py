from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator
import os, json

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# ------------------------- التخزين -------------------------
def load_data():
    if not os.path.exists("special_roles.json"):
        return {"owners": [], "promoters": [], "members": []}
    with open("special_roles.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("special_roles.json", "w") as f:
        json.dump(data, f)

# ------------------- إضافة رافع (فقط المالك) -------------------
@ABH.on(events.NewMessage(pattern=r"^اضافة رافع$"))
async def add_promoter(event):
    if not event.is_group:
        return await event.reply("❗ يعمل فقط في المجموعات.")
    
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة الشخص المراد إضافته كرافع.")
    
    sender = await event.get_sender()
    chat = await event.get_chat()

    try:
        participant = await ABH(GetParticipantRequest(channel=chat.id, participant=sender.id))
        if not isinstance(participant.participant, ChannelParticipantCreator):
            return await event.reply("🚫 فقط مالك المجموعة يمكنه تنفيذ هذا الأمر.")
    except:
        return await event.reply("❗ تعذر التحقق من صلاحياتك.")
    
    user = await r.get_sender()
    data = load_data()
    if user.id not in data["promoters"]:
        data["promoters"].append(user.id)
        save_data(data)
        await event.reply(f"✅ تم إضافة {user.first_name} كـ رافع.")
    else:
        await event.reply("⚠️ هذا المستخدم موجود مسبقاً في قائمة الرافعين.")

# ------------------- رفع مساهم (فقط الرافعين) -------------------
@ABH.on(events.NewMessage(pattern=r"^رفع مساهم$"))
async def promote_member(event):
    if not event.is_group:
        return await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")
    
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة الشخص المراد رفعه.")
    
    sender = await event.get_sender()
    data = load_data()
    if sender.id not in data["promoters"]:
        return await event.reply("🚫 ليس لديك صلاحية تنفيذ هذا الأمر.")
    
    user = await r.get_sender()
    if user.id in data["members"]:
        return await event.reply("⚠️ هذا المستخدم مرفوع مسبقاً.")
    
    data["members"].append(user.id)
    save_data(data)
    await event.reply(f"✅ تم رفع {user.first_name} إلى قائمة المساهمين.")

# ------------------- عرض الرافعين -------------------
@ABH.on(events.NewMessage(pattern=r"^الرافعين$"))
async def show_promoters(event):
    data = load_data()
    if not data["promoters"]:
        return await event.reply("📭 لا يوجد رافعين حتى الآن.")
    
    text = "📋 قائمة الرافعين:\n"
    for uid in data["promoters"]:
        text += f"• [{uid}](tg://user?id={uid})\n"
    await event.reply(text, parse_mode="md")

# ------------------- عرض المساهمين -------------------
@ABH.on(events.NewMessage(pattern=r"^المساهمين$"))
async def show_members(event):
    data = load_data()
    if not data["members"]:
        return await event.reply("📭 لا يوجد مساهمين بعد.")
    
    text = "📋 قائمة المساهمين:\n"
    for uid in data["members"]:
        text += f"• [{uid}](tg://user?id={uid})\n"
    await event.reply(text, parse_mode="md")

# ------------------- حذف مساهم -------------------
@ABH.on(events.NewMessage(pattern=r"^حذف مساهم$"))
async def remove_member(event):
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة العضو المراد حذفه.")
    
    user = await r.get_sender()
    data = load_data()
    if user.id in data["members"]:
        data["members"].remove(user.id)
        save_data(data)
        await event.reply(f"🗑️ تم حذف {user.first_name} من قائمة المساهمين.")
    else:
        await event.reply("⚠️ هذا المستخدم غير موجود في قائمة المساهمين.")

# ------------------- تشغيل البوت -------------------
ABH.run_until_disconnected()
