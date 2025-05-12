import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env (اختياري)
load_dotenv()

# جلب المتغيرات من بيئة النظام
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_NAME = os.environ.get("SESSION_NAME", "session")

# إنشاء كائن TelegramClient
ABH = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# القيم التي تعتبر فوزًا في الألعاب
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

    win = value >= WIN_VALUES.get(emoji, 1000)

    if win:
        await event.reply(f"🎉 مبروك! فزت في لعبة {emoji}\n🔢 النتيجة: `{value}`")
    else:
        await event.reply(f"💔 للأسف، لم تفز في لعبة {emoji}\n🔢 النتيجة: `{value}`")

# بدء العميل
if __name__ == "__main__":
    ABH.start()
    ABH.run_until_disconnected()
