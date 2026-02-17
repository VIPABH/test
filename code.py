from telethon import events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import MessageEntityCustomEmoji, ReactionCustomEmoji
# استيراد العميل الخاص بك
from ABH import ABH as client 

@client.on(events.NewMessage)
async def smart_handler(event):
    # التأكد من وجود entities في الرسالة
    if not event.entities:
        return

    # استخراج أول ايموجي مميز فقط
    custom_emoji = next((e for e in event.entities if isinstance(e, MessageEntityCustomEmoji)), None)

    if custom_emoji:
        emoji_id = custom_emoji.document_id
        try:
            # التفاعل بالإيموجي المميز
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[ReactionCustomEmoji(document_id=emoji_id)]
            ))
            print(f"✅ تم التفاعل بنجاح: {emoji_id}")
        except Exception as e:
            # إذا ظهر خطأ هنا، فالحساب غالباً ليس Premium
            print(f"❌ خطأ أثناء التفاعل: {e}")

print("🚀 البوت شغال.. أرسل إيموجي مميز (Premium) فقط.")
client.run_until_disconnected()
