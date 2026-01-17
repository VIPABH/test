import asyncio
import json
import re
import io
from telethon import TelegramClient, events
from colorama import Fore, Back, Style, init
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import httpx 
from ABH import ABH as client

init(autoreset=True)
console = Console()

# إعدادات الـ API
URL = "https://us-central1-amor-ai.cloudfunctions.net/chatWithGPT"
HEADERS = {
    'User-Agent': "okhttp/5.0.0-alpha.2",
    'Accept-Encoding': "gzip",
    'content-type': "application/json; charset=utf-8"
}

conversation_history = []
code_counter = 0

supported_languages = {
    'python': 'py', 'html': 'html', 'css': 'css', 'javascript': 'js',
    'js': 'js', 'java': 'java', 'c++': 'cpp', 'php': 'php',
    'ruby': 'rb', 'go': 'go', 'bash': 'sh', 'kotlin': 'kt'
}

async def handle_gpt_request(user_message):
    global code_counter
    conversation_history.append({"role": "user", "content": user_message})
    
    payload = {"data": {"messages": conversation_history}}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload, headers=HEADERS, timeout=30.0)
            response_data = response.json()

        # فحص وجود البيانات لتجنب خطأ 'result'
        if response_data and 'result' in response_data and 'choices' in response_data['result']:
            content = response_data['result']['choices'][0]['message']['content']
            conversation_history.append({"role": "assistant", "content": content})
            return content
    except Exception as e:
        console.print(Fore.RED + f"خطأ في الطلب: {e}")
    return None

async def process_and_reply(event, content):
    global code_counter
    code_blocks = re.findall(r'```(.*?)\n(.*?)```', content, re.DOTALL)
    non_code_text = re.sub(r'```.*?```', '', content, flags=re.DOTALL).strip()

    if non_code_text:
        console.print(Fore.GREEN + "رد السيرفر:\n" + Style.RESET_ALL + non_code_text)
        await event.reply(non_code_text)

    for language, code_block in code_blocks:
        code_counter += 1
        language = language.strip().lower()
        ext = supported_languages.get(language, 'py')
        
        syntax = Syntax(code_block.strip(), language if language in supported_languages else "python", theme="dracula", line_numbers=True)
        console.print(Panel(syntax, title=f"Code {code_counter}"))

        file_stream = io.BytesIO(code_block.strip().encode('utf-8'))
        file_stream.name = f"code_{code_counter}.{ext}"
        await event.client.send_file(event.chat_id, file_stream, caption=f"ملف الكود رقم {code_counter}")

# إعدادات الدخول (Telethon)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("مرحباً بك! أنا بوت GPT المطور بـ Telethon. أرسل سؤالك الآن.")

@client.on(events.NewMessage(incoming=True, func=lambda e: not e.text.startswith('/')))
async def chatter(event):
    async with client.action(event.chat_id, 'typing'):
        response_content = await handle_gpt_request(event.text)
        if response_content:
            await process_and_reply(event, response_content)
        else:
            await event.reply("⚠️ السيرفر مشغول أو لم يرسل بيانات صحيحة.")

console.print(Fore.GREEN + "البوت يعمل الآن عبر Telethon...")
client.run_until_disconnected()
