from telethon import TelegramClient, events
import asyncio
from deepseek_api import DeepSeekAI  # استخدم الكلاس المذكور أعلاه
from ABH import ABH as bot
# إعدادات التليجرام

# إعدادات DeepSeek
DEEPSEEK_API_KEY = 'sk-531f6b796ad24749b26d68e6d1d74a88'

# تهيئة العميل
ai = DeepSeekAI(DEEPSEEK_API_KEY)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("مرحباً! أنا بوت DeepSeek الذكي. أرسل لي أي سؤال وسأجيبك.")

@bot.on(events.NewMessage)
async def handle_message(event):
    if event.is_private or event.text.startswith('/ask'):
        # إظهار "يكتب..." أثناء معالجة الرسالة
        async with bot.action(event.chat_id, 'typing'):
            response = ai.chat_completion(event.text)
            await event.reply(response)

async def main():
    await bot.start()
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
