from telethon import TelegramClient, events, Button
import os
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

@client.on(events.InlineQuery)
async def inline_query_handler(event):
    builder = event.builder
    query = event.text

    if query.strip(): 
        parts = query.split(' ')
        if len(parts) >= 2: 
            message = ' '.join(parts[:-1]) 
            username = parts[-1] 
            
            if not username.startswith('@'):
                username = f'@{username}'
            
            try:
                whisper_id = f"{event.sender_id}:{username}"
                store_whisper(whisper_id, event.sender_id, username, message)

                result = builder.article(
                    title='اضغط لارسال الهمسة',
                    description=f'إرسال الرسالة إلى {username}',
                    text=f"همسة سرية إلى \n الله يثخن اللبن عمي ({username})",
                    buttons=[Button.inline(text='tap to see', data=f'send:{username}:{message}:{event.sender_id}:{whisper_id}')]
                )
            except Exception:
                result = builder.article(
                    title='لرؤية المزيد حول الهمس',
                    description="همس",
                    text='اضغط هنا'
                )
        else:
            result = builder.article(
                title='خطأ في التنسيق',
                description="يرجى استخدام التنسيق الصحيح: @username <message>",
                text='التنسيق غير صحيح، يرجى إرسال الهمسة بالتنسيق الصحيح: @username <message>'
            )
        await event.answer([result])

@client.on(events.CallbackQuery)
async def callback_query_handler(event):
    data = event.data.decode('utf-8')
    if data.startswith('send:'):
        _, username, message, sender_id, whisper_id = data.split(':', 4)
        try:
            whisper = get_whisper(whisper_id)

            if whisper:
                if f"@{event.sender.username}" == username or str(event.sender_id) == sender_id:
                    await event.answer(f"{whisper.message}", alert=True)
                else:
                    await event.answer("هذه الرسالة ليست موجهة لك!", alert=True)
            else:
                await event.answer("لم يتم العثور على الهمسة!", alert=True)

        except Exception as e:
            await event.answer(f'حدث خطأ: {str(e)}', alert=True)

def store_whisper(whisper_id, sender_id, username, message):
    # Store the whisper details in a database or a file
    print(f"Storing whisper: {whisper_id}, {sender_id}, {username}, {message}")
def get_whisper(whisper_id):
    # Retrieve the whisper details from a database or a file
    print(f"Retrieving whisper: {whisper_id}")
    return None
    return None

client.run_until_disconnected()
