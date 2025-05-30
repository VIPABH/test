import os
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# تحميل البيانات من ملف .env
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء جلسة البوت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تأكد من وجود مجلد التخزين المؤقت
if not os.path.exists("anti_ban"):
    os.makedirs("anti_ban")

@bot.on(events.ChatAction)
async def anti_mass_ban(event):
    if event.user_added or event.user_joined or not event.kicked:
        return

    if not event.chat or not event.action_message:
        return

    # معرف الشخص الذي نفّذ الحظر
    executor = event.action_message.from_id.user_id if event.action_message.from_id else None
    if not executor or executor == (await bot.get_me()).id:
        return

    now = time.time()
    file_path = f"anti_ban/{executor}.txt"

    # تحميل السجلات القديمة من الملف
    timestamps = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            timestamps = [float(line.strip()) for line in f.readlines()]

    # حذف السجلات الأقدم من 5 ثواني
    timestamps = [t for t in timestamps if now - t <= 5]
    timestamps.append(now)

    # حفظ السجلات الجديدة
    with open(file_path, "w") as f:
        for t in timestamps:
            f.write(f"{t}\n")

    # إذا تجاوز عدد الحظرات 5 خلال 5 ثواني
    if len(timestamps) > 5:
        try:
            await bot.edit_permissions(
                event.chat_id,
                executor,
                view_messages=False  # كتم المستخدم
            )
            await event.reply(f"🚫 تم كتم [{executor}](tg://user?id={executor}) لأنه قام بحظر أكثر من 5 أعضاء خلال 5 ثواني.")
        except Exception as e:
            await event.reply(f"❌ فشل في كتم المستخدم: {e}")

bot.run_until_disconnected()
