import os
import time
from telethon import TelegramClient, events
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
def anti_abuse(func):
    @wraps(func)
    async def wrapper(event):
        if not event.is_group:
            return await func(event)

        # نتحقق من وجود المعطى في group(1)
        target = event.pattern_match.group(1)
        if not target:
            return await func(event)

        # يمكن إضافة تحقق على شكل target (مثل يبدأ بـ @)
        if not target.startswith("@"):
            return await func(event)

        sender = await event.get_sender()
        user_id = sender.id
        chat_id = event.chat_id
        now = time.time()

        # ملف لتخزين التوقيتات بناءً على user_id + target (لكل هدف بشكل منفصل)
        safe_target = target.replace("@", "")  # لتجنب مشاكل في اسم الملف
        file_path = f"anti_ban/{chat_id}_{user_id}_{safe_target}.txt"

        timestamps = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                timestamps = [float(line.strip()) for line in f if line.strip()]

        # إزالة السجلات الأقدم من 5 ثواني
        timestamps = [t for t in timestamps if now - t <= 5]
        timestamps.append(now)

        with open(file_path, "w") as f:
            for t in timestamps:
                f.write(f"{t}\n")

        # إذا تجاوز عدد الاستخدام 5 مرات خلال 5 ثواني
        if len(timestamps) > 5:
            try:
                await bot.edit_permissions(
                    chat_id,
                    user_id,
                    view_messages=False,
                    until_date=datetime.utcnow() + timedelta(minutes=10)
                )
                await event.reply(
                    f"🚫 تم كتم [{sender.first_name}](tg://user?id={user_id}) لمدة 10 دقائق بسبب تكرار أوامر الحظر على {target}."
                )
                return
            except Exception as e:
                await event.reply(f"❌ فشل في تنفيذ الإجراء: {e}")
                return

        return await func(event)
    return wrapper
@bot.on(events.NewMessage(pattern=r'^(?:[./]?)(?:حظر|ban) (@[\w\d_]+)$'))
@anti_abuse
async def ban_user(event):
    target = event.pattern_match.group(1)
    await event.reply(f"تم استلام أمر حظر للمستخدم: {target}")
bot.run_until_disconnected()
