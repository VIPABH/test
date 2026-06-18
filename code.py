from telethon import events
from telethon.tl import types  
from ABH import *
from telethon import events

import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode

# ضع التوكين الخاص بك هنا


bot = Bot(token=bot_token)
dp = Dispatcher()

# استخدام اسم المستخدم (بدون @) للفلترة الأدق
BOT_USERNAME = "Hauehshbot"

@dp.message(F.text.contains(f"@{BOT_USERNAME}")) 
async def handle_mention(message: types.Message):
    await message.reply("مرحباً! أنا Guest Bot، لقد تم استدعائي للتو.")

@dp.message(F.reply_to_message)
async def handle_reply(message: types.Message):
    # التحقق من أن الرسالة التي تم الرد عليها هي من البوت الخاص بنا
    bot_user = await bot.get_me()
    if message.reply_to_message.from_user.id == bot_user.id:
        await message.reply("شكراً لردك! كيف يمكنني مساعدتك؟")

async def main():
    print("البوت يعمل الآن...")
    # حذف أي تحديثات قديمة عند البدء
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())




    
# @ABH.on(events.NewMessage(pattern="تيست"))
# async def test(e):
#     # إرسال رسالة أولية للمستخدم توضح أن العملية بدأت
#     status_msg = await e.reply("جاري فحص الرسائل، يرجى الانتظار...")
    
#     # تحديد نطاق المعرفات
#     ids = list(range(502, 633)) 
    
#     # جلب الرسائل
#     messages = await ABH.get_messages("x04ou", ids=ids)
    
#     found = 0
#     deleted = 0
    
#     # فرز الرسائل
#     for msg in messages:
#         if msg is not None:
#             found += 1
#         else:
#             deleted += 1
            
#     # تحديث النتيجة للمستخدم
#     await status_msg.edit(
#         f"✅ **تم فحص الرسائل:**\n\n"
#         f"📌 **الرسائل الموجودة:** {found}\n"
#         f"🗑 **الرسائل المحذوفة:** {deleted}\n"
#         f"📊 **إجمالي النطاق:** {len(ids)}"
#     )
