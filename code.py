from telethon import events
from telethon.tl import types  
from ABH import *
@client.on(events.InlineQuery)
async def inline_handler(event):
    # الحصول على النص الذي كتبه المستخدم بعد يوزر البوت
    query = event.text
    
    # بناء نتيجة الرد التي ستظهر للمستخدم
    builder = event.builder
    result = builder.article(
        title='مرحباً بك!',
        text=f'أهلاً بك! لقد طلبت البوت الخاص بي، والـ ID الخاص بك هو: {event.sender_id}',
        description='اضغط هنا لإرسال رد البوت'
    )
    
    # إرسال النتيجة
    await event.answer([result])




    
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
