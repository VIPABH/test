from telethon import events
from telethon.tl import types  
from ABH import *
from telethon import events

client = ABH

@client.on(events.NewMessage)
async def handler(event):
    # يتحقق البوت إذا تم ذكره (@botname) أو الرد عليه
    # بما أن البوت في وضع الضيف، لن تصله أي رسالة أخرى
    
    # يمكنك الرد مباشرة على الرسالة التي استدعت البوت
    await event.reply("مرحباً! أنا أعمل الآن في وضع الضيف (Guest Mode).")

print("البوت يعمل الآن...")


    
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
