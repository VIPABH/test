import os
import time
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تخزين بيانات كل مستخدم: عداد الحظر وأول وقت حظر في النافذة الزمنية
user_ban_data = {}

@ABH.on(events.NewMessage(pattern='^(حظر|.حظر|حظر$|/حظر)(.*)'))
async def anti_spam_ban(event):
    user_id = event.sender_id
    now = time.time()

    # قراءة الجزء المرفق بعد الأمر (مثلاً اسم المستخدم أو المعرف)
    target = event.pattern_match.group(2).strip()

    if not target:
        await event.reply("**يرجى تحديد المستخدم الذي تريد حظره.**")
        return

    # تهيئة بيانات المستخدم إن لم تكن موجودة
    if user_id not in user_ban_data:
        user_ban_data[user_id] = {"count": 0, "first_time": now}

    data = user_ban_data[user_id]

    # إذا مرت أكثر من 5 ثواني على أول عملية حظر، إعادة التهيئة
    if now - data["first_time"] > 5:
        data["count"] = 0
        data["first_time"] = now

    # زيادة عداد الحظر
    data["count"] += 1

    # تنفيذ عملية الحظر (هنا فقط رد مؤقت، يمكنك تعديلها لتنفيذ حظر فعلي)
    await event.reply(f"**جاري حظر {target}**")

    # إذا تجاوز المستخدم 5 حظرات خلال 5 ثواني
    if data["count"] >= 5:
        try:
            # تقييد المستخدم نفسه في نفس الشات (كتم ومنع إرسال رسائل)
            rights = ChatBannedRights(
                until_date=None,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
            await ABH(EditBannedRequest(event.chat_id, user_id, rights))
            await event.reply(f"🚫 تم تقييد المستخدم [{user_id}](tg://user?id={user_id}) بسبب تكرار الحظر خلال 5 ثوانٍ.")
            # إعادة تهيئة العداد بعد التقييد
            user_ban_data[user_id] = {"count": 0, "first_time": now}
        except Exception as e:
            await event.reply(f"❌ فشل في تقييد المستخدم: {e}")

ABH.run_until_disconnected()
