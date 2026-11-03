from ABH import ABH as client
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, ReactionCustomEmoji
from telethon.tl.functions.messages import SendReactionRequest

@client.on(events.NewMessage(pattern=r'^\.تفاعل_مميز\s+(\d+)$'))
async def custom_reaction_handler(event):
    """
    أمر مستمع لتجربة التفاعل المميز
    الاستخدام بالرد على أي رسالة:
    .تفاعل_مميز 5432109876543210
    """
    # التأكد من أن الأمر مرفوع بالرد على رسالة
    if not event.is_reply:
        await event.reply("⚠️ يجب الرد على الرسالة التي تريد التفاعل معها!")
        return

    # استخراج آيدي التفاعل المميز (Document ID) المرسل مع الأمر
    custom_doc_id = int(event.pattern_match.group(1))
    
    # جلب الرسالة المستهدفة وآيدي القناة/المحادثة
    reply_msg = await event.get_reply_message()
    chat_id = event.chat_id
    msg_id = reply_msg.id

    await event.reply(f"⏳ جاري إرسال التفاعل المميز بالآيدي: `{custom_doc_id}`...")

    try:
        # معالجة الآيدي سواء كان سالباً (قناة/مجموعة) أو موجباً
        clean_chat = str(chat_id).lstrip('-')
        if clean_chat.isdigit() and str(chat_id).startswith('-'):
            peer = PeerChannel(int(chat_id))
        else:
            peer = await event.get_input_chat()

        # إرسال التفاعل المميز
        await client(SendReactionRequest(
            peer=peer,
            msg_id=msg_id,
            reaction=[ReactionCustomEmoji(document_id=custom_doc_id)],
            big=False
        ))
        
        
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء إرسال التفاعل:\n`{str(e)}`")

# تشغيل البوت أو الجلسة
print("البوت يعمل الآن...")
