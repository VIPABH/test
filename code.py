from ABH import ABH as client
from telethon import  events


@client.on(events.NewMessage(pattern=r'^/reactions$|^تفاعلات$'))
async def check_reply_reactions(event):
    reply_message = await event.get_reply_message()
    
    if not reply_message:
        await event.reply("❌ يرجى الرد على الرسالة التي تريد معرفة تفاعلاتها!")
        return

    # 🔑 الخطوة الحاسمة: إعادة جلب الرسالة بالكامل من السيرفر لتحديث بيانات التفاعلات والمشاهدات
    full_message = await client.get_messages(event.chat_id, ids=reply_message.id)

    # التحقق من وجود تفاعلات بعد الجلب الكامل
    if not full_message or not full_message.reactions:
        await event.reply("ℹ️ لا توجد تفاعلات على هذه الرسالة (أو لم يتم تحميلها).")
        return

    text = "📊 **التفاعلات الحقيقية على الرسالة:**\n\n"
    
    for count in full_message.reactions.results:
        reaction = count.reaction
        if hasattr(reaction, 'emoticon'):
            emoji = reaction.emoticon
        else:
            emoji = "إيموجي مخصص"
            
        total_count = count.count
        text += f"• الإيموجي: {emoji} ⟵ العدد: **{total_count}**\n"

    await event.reply(text)
