from telethon import events, Button
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import MessageEntityCustomEmoji, ReactionCustomEmoji
# استيراد العميل الخاص بك
from ABH import ABH as client 

@client.on(events.NewMessage)
async def smart_handler(event):
    # --- الجزء الأول: التفاعل التلقائي بالإيموجي المميز ---
    if event.entities:
        for entity in event.entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                emoji_id = entity.document_id
                try:
                    await client(SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=event.id,
                        reaction=[ReactionCustomEmoji(document_id=emoji_id)]
                    ))
                    print(f"✅ تم التفاعل بالإيموجي: {emoji_id}")
                    
                    # --- الجزء الثاني: تجربة الأزرار الملونة (تحديث واجهة البوتات) ---
                    # ملاحظة: استبدل الـ ID بـ ID إيموجي شغال عندك
                    buttons = [
                        [
                            Button.inline("زر أخضر (نجاح)", data="success", 
                                          style='success', icon_custom_emoji_id=emoji_id),
                            Button.inline("زر أحمر (خطر)", data="danger", 
                                          style='danger', icon_custom_emoji_id=emoji_id)
                        ],
                        [
                            Button.inline("زر أزرق (أساسي)", data="primary", 
                                          style='primary', icon_custom_emoji_id=5445105244111314944)
                        ]
                    ]
                    
                    await event.reply("🚀 شوف التحديثات الجديدة (أزرار ملونة وإيموجي مخصص):", buttons=buttons)
                    
                except Exception as e:
                    print(f"❌ خطأ: {e}")
                break

print("🚀 البوت شغال.. أرسل إيموجي مميز لتجربة التفاعل والأزرار الملونة!")
