import os
from telethon import TelegramClient, events

# جلب متغيرات البيئة
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء العميل
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# قيم الفوز الثابتة لكل لعبة
WIN_VALUES = {
    "🎲": 6,
    "🎯": 6,
    "🏀": 5,
    "⚽": 5,
    "🎳": 6,
    "🎰": 64
}

@ABH.on(events.NewMessage(pattern='🎲|🎯|🏀|⚽|🎳|🎰'))
async def telegramgames(event):
    if not event.message.dice:
        return

    dice = event.message.dice
    emoji = dice.emoticon
    value = dice.value

    # تحقق دقيق من الفوز حسب القيمة الفائزة
    win = value == WIN_VALUES.get(emoji, -1)

    if win:
        await event.reply(f"🎉 مبروك! فزت في لعبة {emoji}\n🔢 النتيجة: `{value}`")
    else:
        await event.reply(f"💔 للأسف، لم تفز في لعبة {emoji}\n🔢 النتيجة: `{value}`")

# بدء العميل
if __name__ == "__main__":
    ABH.start()
    ABH.run_until_disconnected()
