from telethon import TelegramClient, events
import os
import db
# إعداد بيانات الاتصال
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
bot_token = os.getenv('BOT_TOKEN')

# التحقق من وجود API_ID و API_HASH و BOT_TOKEN
if not api_id or not api_hash or not bot_token:
    raise ValueError("مفقود واحد أو أكثر من المتغيرات البيئية: API_ID, API_HASH, BOT_TOKEN")

# تحويل API_ID إلى عدد صحيح
api_id = int(api_id)

# إنشاء جلسة TelegramClient
ABH = TelegramClient('c', api_id, api_hash).start(bot_token=bot_token)

# أمر "سماح" لإضافة المستخدم إلى قائمة المسموح لهم بالتعديلات
@ABH.on(events.NewMessage(pattern='سماح'))
async def approve_user(event):
    if event.is_group:  # التأكد من أن الرسالة في مجموعة
        if event.is_reply:  # إذا كانت الرسالة ردًا
            reply_message = await event.get_reply_message()
            user_id = reply_message.sender_id  # استخراج معرف المستخدم من الرسالة التي تم الرد عليها
            
            # إضافة المستخدم إلى قائمة المسموح لهم باستخدام الدالة من db.py
            add_approved_user(user_id)
            await event.reply(f"✅ تم السماح للمستخدم {user_id} بالتعديلات.")
        else:
            await event.reply("❗ يرجى الرد على رسالة المستخدم الذي تريد السماح له بالتعديلات.")
    else:
        await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")

# أمر "إلغاء سماح" لإزالة المستخدم من قائمة المسموح لهم بالتعديلات
@ABH.on(events.NewMessage(pattern='إلغاء سماح'))
async def disapprove_user(event):
    if event.is_group:  # التأكد من أن الرسالة في مجموعة
        if event.is_reply:  # إذا كانت الرسالة ردًا
            reply_message = await event.get_reply_message()
            user_id = reply_message.sender_id  # استخراج معرف المستخدم من الرسالة التي تم الرد عليها
            
            # إزالة المستخدم من قائمة المسموح لهم باستخدام الدالة من db.py
            remove_approved_user(user_id)
            await event.reply(f"❌ تم إلغاء السماح للمستخدم {user_id} بالتعديلات.")
        else:
            await event.reply("❗ يرجى الرد على رسالة المستخدم الذي تريد إلغاء السماح له بالتعديلات.")
    else:
        await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")

# أمر لعرض قائمة المسموح لهم
@ABH.on(events.NewMessage(pattern='قائمة المسموح لهم'))
async def list_approved_users(event):
    if event.is_group:  # التأكد من أن الرسالة في مجموعة
        approved_users = get_approved_users()  # استرجاع قائمة المسموح لهم باستخدام الدالة من db.py
        if approved_users:
            approved_list = "\n".join([str(user_id[0]) for user_id in approved_users])
            await event.reply(f"📝 قائمة المستخدمين المسموح لهم بالتعديلات:\n{approved_list}")
        else:
            await event.reply("❗ لا يوجد أي مستخدمين مسموح لهم بالتعديلات حالياً.")
    else:
        await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")

# معالجة الرسائل المعدلة
@ABH.on(events.MessageEdited)
async def echo(event):
    if event.is_group:  # التأكد من أن الرسالة في مجموعة
        user_id = event.sender_id
        approved_users = get_approved_users()  # استرجاع قائمة المسموح لهم باستخدام الدالة من db.py
        approved_user_ids = [user_id[0] for user_id in approved_users]
        if user_id in approved_user_ids:  # التحقق مما إذا كان المستخدم مسموحًا له بالتعديل
            return  # السماح بالتعديل بدون أي رد
        elif event.message.media:  # إذا كان المستخدم غير مسموح وكان هناك وسائط
            await event.reply("ها ههههه سالمين")
        else:
            return  # لا تفعل شيئًا إذا لم تكن هناك وسائط
    else:
        return  # لا تفعل شيئًا إذا كانت الرسالة في محادثة خاصة

# تشغيل العميل
ABH.run_until_disconnected()
