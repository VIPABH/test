import os
from telethon import TelegramClient, events

# جلب المتغيرات من البيئة
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# التحقق من وجود المتغيرات
if not all([api_id, api_hash, bot_token]):
    raise ValueError("❌ تأكد من ضبط متغيرات البيئة: API_ID, API_HASH, BOT_TOKEN")

# إنشاء كائن العميل
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# قيم الفوز لكل لعبة
WIN_VALUES = {
    "🎲": 6,    # نرد
    "🎯": 6,    # سهم
    "🏀": 5,    # سلة
    "⚽": 5,    # كرة
    "🎳": 6,    # بولينغ
    "🎰": 64    # سلوت ماشين
}

@ABH.on(events.NewMessage(pattern='🎲|🎯|🏀|⚽|🎳|🎰'))
async def telegramgames(event):
    if not event.message.dice:
        return

    dice = event.message.dice
    emoji = dice.emoticon
    value = dice.value

    # التحقق من الفوز حسب القيمة الثابتة
    win = value == WIN_VALUES.get(emoji, -1)

    if win:
        await event.reply(f"🎉 مبروك! فزت في لعبة {emoji}\n🔢 النتيجة: `{value}`")
    else:
        await event.reply(f"💔 للأسف، لم تفز في لعبة {emoji}\n🔢 النتيجة: `{value}`")

# تشغيل البوت
if __name__ == "__main__":
    ABH.start()
    ABH.run_until_disconnected()
