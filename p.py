import os
from telethon import TelegramClient, events
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
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
