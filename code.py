from ABH import ABH as client
from telethon import  events

from telethon import TelegramClient, events
from telethon.tl.types import ReactionEmoji

@client.on(events.NewMessage(pattern=r'^/reactions$|^تفاعلات$'))
async def react_like_target(event):
    # 1. جلب الرسالة المردود عليها
    reply_message = await event.get_reply_message()
    
    if not reply_message:
        await event.reply("❌ يرجى الرد على الرسالة المطلوب نسخ تفاعلها!")
        return

    # 2. إعادة جلب الرسالة لضمان تحديث البيانات
    full_message = await client.get_messages(reply_message.peer_id, ids=reply_message.id)
    await event.reply(str(full_message))
    if not full_message or not full_message.reactions:
        await event.reply("ℹ️ لا توجد تفاعلات على الرسالة المردود عليها لتكرارها.")
        return

    # 3. استخراج أول إيموجي تفاعل موجود على الرسالة
    first_reaction_count = full_message.reactions.results[0]
    reaction_obj = first_reaction_count.reaction

    try:
        # إذا كان إيموجي قياسي (Standard Emoji)
        if hasattr(reaction_obj, 'emoticon'):
            emoji_str = reaction_obj.emoticon
            
            # إرسال التفاعل (وضع نفس الإيموجي على الرسالة المردود عليها)
            await client.send_reaction(
                entity=full_message.peer_id,
                message=full_message.id,
                reaction=ReactionEmoji(emoticon=emoji_str)
            )
            
            await event.reply(f"✅ تم إضافة التفاعل {emoji_str} على الرسالة بنجاح!")
        else:
            await event.reply("⚠️ التفاعل الموجود هو إيموجي مخصص (Custom Emoji) ولا يمكن للبوت العادي استخدامه.")

    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء إرسال التفاعل: {e}")
