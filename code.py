from ABH import *
x = []

@ABH.on(events.NewMessage)
async def handler(e):
    id = e.sender_id
    if id not in x:
        x.append(id)
        await e.reply("Hello")
    
    if len(x) == 10:
        # الحصول على كائنات المستخدمين للقائمة كاملة
        users = await ABH.get_entity(x)
        
        # تحويل القائمة إلى نص يحتوي على أسماء المستخدمين مثلاً
        msg_text = "قائمة أول 10 مستخدمين تواصلوا معي:\n"
        for user in users:
            msg_text += f"- {user.first_name} (ID: {user.id})\n"
        
        # الآن نرسل النص (String) وليس الكائن
        await e.reply(msg_text)
        
        # اختيار اختياري: تصفير القائمة إذا أردت البدء من جديد
        # x.clear()
