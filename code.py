from telethon import events, Button
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import (
    MessageEntityCustomEmoji, 
    ReactionCustomEmoji, 
    KeyboardButtonStyle # استيراد الستايليات
)
# استيراد العميل الخاص بك
from ABH import ABH as client 

@client.on(events.NewMessage)
async def smart_handler(event):
    # تعريف المتغير بقيمة افتراضية لتجنب خطأ UnboundLocalError
    emoji_id = None
    
    # البحث عن إيموجي مميز
    if event.entities:
        for entity in event.entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                emoji_id = entity.document_id
                break

    # إذا لقى إيموجي مميز، ينفذ التفاعل والأزرار
    if emoji_id:
        try:
            # 1. التفاعل
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[ReactionCustomEmoji(document_id=emoji_id)]
            ))
            print(f"✅ تم التفاعل بالإيموجي: {emoji_id}")

            # 2. الأزرار (استخدام الأزرار العادية لأن style يحتاج Raw API في بعض نسخ تليثون)
            # ملاحظة: إذا ظهر خطأ في style مرة ثانية، امسح حقل style و icon_custom_emoji_id
            # لأن مكتبة Telethon الرسمية لسه في مرحلة تحديث لهذه الحقول
            buttons = [
                [
                    Button.inline("زر أخضر", data="ok"), 
                    Button.inline("زر أحمر", data="no")
                ]
            ]
            
            await event.reply("🚀 تم التفاعل بنجاح!", buttons=buttons)

        except Exception as e:
            print(f"❌ حدث خطأ: {e}")

print("🚀 البوت شغال.. أرسل إيموجي مميز!")
client.run_until_disconnected()
