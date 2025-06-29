from telethon import TelegramClient, events
import asyncio, requests
class DeepSeekAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, prompt, model="deepseek-chat", temperature=0.7, max_tokens=2000):
        """
        إرسال رسالة إلى نموذج DeepSeek والحصول على رد
        """
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"خطأ في الاتصال بالخادم: {str(e)}"
        except KeyError:
            return "خطأ في معالجة الرد من الخادم"
        except Exception as e:
            return f"حدث خطأ غير متوقع: {str(e)}"
from ABH import ABH as bot

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
