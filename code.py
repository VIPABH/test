from telethon import events
from telethon.tl import types  
from ABH import *
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
@ABH.on(events.NewMessage)
async def smart_filter(e):
    # إذا كانت الرسالة من "بوت" أو "مستخدم مشبوه"
    # وتحتوي على أزرار (ReplyInlineMarkup)
    if e.reply_markup and isinstance(e.reply_markup, types.ReplyInlineMarkup):
        
        # استخراج الروابط للتحليل
        for row in e.reply_markup.rows:
            for btn in row.buttons:
                # إذا وجدنا رابطاً في زر
                if hasattr(btn, 'url'):
                    # نبهني فقط، ولا تحظر (كما طلبت)
                    await e.reply( f"🚨 تم التقاط رسالة سبام! رابط الأزرار: {btn.url}")
                    return # الخروج من الفلتر
