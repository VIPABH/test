from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import MessageEntityCustomEmoji, ReactionCustomEmoji

# معلومات الحساب
api_id = 123456
api_hash = 'your_api_hash'

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage)
async def auto_react_custom_emoji(event):
    # التأكد من أن الرسالة تحتوي على "entities" (وهي التي تحمل بيانات الإيموجي المميز)
    if event.entities:
        for entity in event.entities:
            # التحقق إذا كان الكيان هو إيموجي مخصص
            if isinstance(entity, MessageEntityCustomEmoji):
                emoji_id = entity.document_id
                
                try:
                    # التفاعل باستخدام المعرف الذي تم التقاطه تلقائياً
                    await client(SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=event.id,
                        reaction=[ReactionCustomEmoji(document_id=emoji_id)]
                    ))
                    print(f"تم التفاعل بنجاح بالإيموجي: {emoji_id}")
                except Exception as e:
                    print(f"خطأ أثناء التفاعل: {e}")
                
                # نكتفي بأول إيموجي مميز نلقاه في الرسالة
                break 

print("البوت شغال.. أرسل أي إيموجي مميز وسيتفاعل البوت به فوراً!")
client.start()
client.run_until_disconnected()
