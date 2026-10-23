from ABH import ABH as client

# ... إعداد الـ client والتسجيل ...

@client.on(events.NewMessage(pattern=r'^/reactions$|^تفاعلات$'))
async def check_reply_reactions(event):
    # التأكد من أن المستخدم قام بالرد على رسالة
    reply_message = await event.get_reply_message()
    
    if not reply_message:
        await event.reply("❌ يرجى الرد على الرسالة التي تريد معرفة تفاعلاتها!")
        return

    # فحص ما إذا كانت الرسالة المردود عليها تحتوي على تفاعلات
    if not reply_message.reactions:
        await event.reply("ℹ️ لا توجد أي تفاعلات على هذه الرسالة.")
        return

    # تجهيز النص المنسق للتفاعلات
    text = "📊 **التفاعلات على هذه الرسالة:**\n\n"
    
    for count in reply_message.reactions.results:
        # معرفة نوع الإيموجي (عادي أم مخصص/بريميوم)
        reaction = count.reaction
        if hasattr(reaction, 'emoticon'):
            emoji = reaction.emoticon
        else:
            emoji = "إيموجي مخصص"
            
        total_count = count.count
        text += f"• الإيموجي: {emoji} ⟵ العدد: **{total_count}**\n"

    # إرسال النتيجة رداً على المستخدم
    await event.reply(text)
