import os
from telethon import TelegramClient, events, Button

# جلب القيم من المتغيرات البيئية
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء جلسة للبوت
ABH = TelegramClient('c', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.InlineQuery)
async def inline_query_handler(event):
    builder = event.builder
    query = event.text.strip()

    if query:
        parts = query.split(' ')
        if parts[0] == 'تيل' and len(parts) >= 3:
            message = ' '.join(parts[1:-1])  # استخراج الرسالة
            username = parts[-1]  # استخراج اسم المستخدم

            if not username.startswith('@'):
                username = f'@{username}'

            try:
                reciver = await ABH.get_entity(username)  # جلب معلومات المستلم
                reciver_id = reciver.id  # ID المستخدم المستلم
                sender_id = event.query.user_id  # معرف المرسل

                # إنشاء الاستجابة مع زر
                result = builder.article(
                    title='📩 إرسال رسالة سرية',
                    description=f'تم إرسال الرسالة إلى {username}',
                    text=f"🔹 الرسالة التي سيتم إرسالها إلى {username} هي:\n\n{message}",
                    buttons=[
                        [Button.inline("إرسال الرسالة", data=f"send:{reciver_id}:{message}")]
                    ],
                    link_preview=False
                )

                # إرسال تأكيد للمرسل في محادثة البوت
                await ABH.send_message(
                    sender_id,
                    f"✅ **تم إنشاء الرسالة إلى {username}!**\n"
                    f"💬 **الرسالة:** {message}"
                )

            except Exception as e:
                result = builder.article(
                    title='❌ خطأ في الإرسال',
                    description="حدث خطأ أثناء معالجة طلبك.",
                    text="حدث خطأ أثناء معالجة طلبك، الرجاء المحاولة مرة أخرى."
                )
        else:
            return

        await event.answer([result])

@ABH.on(events.CallbackQuery)
async def callback_query_handler(event):
    data = event.data.decode('utf-8')
    if data.startswith('send:'):
        _, reciver_id, message = data.split(':')
        reciver_id = int(reciver_id)
        sender_id = event.query.user_id

        # إرسال الرسالة إلى المستخدم المستهدف مباشرة عند الضغط
        await ABH.send_message(
            reciver_id,
            f"📩 **لديك رسالة سرية من شخص مجهول!**\n"
            f"💬 **الرسالة:** {message}"
        )

        # # إرسال تأكيد للمرسل في محادثة البوت
        # await ABH.send_message(
        #     sender_id,
        #     f"✅ **تم إرسال الرسالة إلى المستخدم بنجاح!**\n"
        #     f"💬 **الرسالة:** {message}"
        # )

print("✅ Bot is running...")
ABH.run_until_disconnected()
