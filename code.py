from telethon import events
from ABH import ABH  # استيراد العميل باسم ABH

target_file_id = None  # نخزن هنا الـ file_id للمتحرك

# أمر لتعيين الـ file_id عبر الرد
@ABH.on(events.NewMessage(pattern=r"^/ض$"))
async def set_file_id(event):
    global target_file_id
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.document:
            target_file_id = reply_msg.file.id
            await event.reply("✅ تم حفظ المتحرك.")
        else:
            await event.reply("❌ الرد يجب أن يكون على متحرك.")
    else:
        await event.reply("❌ يجب الرد على المتحرك.")

# مراقبة الرسائل وحذف أي رسالة بنفس الـ file_id
@ABH.on(events.NewMessage)
async def delete_matching(event):
    global target_file_id
    if target_file_id and event.document:
        if event.file.id == target_file_id:
            # حذف الرسالة الحالية
            await event.delete()

            # إذا كانت هذه الرسالة رد على رسالة أخرى، نحذف الرسالة الأصلية أيضًا
            reply_msg = await event.get_reply_message()
            if reply_msg:
                await reply_msg.delete()

print("Bot is running...")
ABH.run_until_disconnected()
