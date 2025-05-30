import os
import time
from telethon import TelegramClient, events
from dotenv import load_dotenv

# تحميل بيانات البوت من .env
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء جلسة البوت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# إنشاء مجلد لتخزين بيانات الاستخدام المؤقتة
if not os.path.exists("anti_ban"):
    os.makedirs("anti_ban")

@bot.on(events.NewMessage(pattern="حظر"))
async def anti_spam_ban_word(event):
    if not event.is_group and not event.is_channel:
        return

    sender = await event.get_sender()
    user_id = sender.id
    chat_id = event.chat_id
    now = time.time()
    file_path = f"anti_ban/{chat_id}_{user_id}.txt"

    # تحميل سجل الرسائل السابقة التي تحتوي على "حظر"
    timestamps = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            timestamps = [float(line.strip()) for line in f.readlines()]

    # إبقاء السجلات التي حدثت خلال آخر 5 ثوانٍ فقط
    timestamps = [t for t in timestamps if now - t <= 5]
    timestamps.append(now)

    # حفظ السجلات الجديدة
    with open(file_path, "w") as f:
        for t in timestamps:
            f.write(f"{t}\n")

    # إذا كتب المستخدم كلمة "حظر" أكثر من 5 مرات خلال 5 ثواني
    if len(timestamps) > 5:
        try:
            await bot.edit_permissions(
                chat_id,
                user_id,
                view_messages=False  # كتمه
            )
            await event.reply(f"🚫 تم كتم [{user_id}](tg://user?id={user_id}) لأنه أرسل كلمة 'حظر' أكثر من 5 مرات خلال 5 ثوانٍ.")
        except Exception as e:
            await event.reply(f"❌ فشل في كتم المستخدم: {e}")

bot.run_until_disconnected()
