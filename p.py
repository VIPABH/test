import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

WIN_VALUES = {
    "🎲": 6,
    "🎯": 6,
    "🏀": 5,
    "⚽": 5,
    "🎳": 6,
    "🎰": 64
}

@ABH.on(events.NewMessage())
async def telegramgames(event):
    a = event.text
    print(a)
    if not event.message.dice:
        return

    dice = event.message.dice
    emoji = dice.emoticon
    value = dice.value
    print(f"📥 تلقينا لعبة: {emoji} | القيمة: {value}")  # للمتابعة في الطرفية

    win = value == WIN_VALUES.get(emoji, -1)

    if win:
        await event.reply(f"🎉 مبروك! فزت في لعبة {emoji}\n🔢 النتيجة: `{value}`")
    else:
        await event.reply(f"💔 للأسف، لم تفز في لعبة {emoji}\n🔢 النتيجة: `{value}`")

if __name__ == "__main__":
    print("✅ بدأ البوت بنجاح ...")
    ABH.run_until_disconnected()
