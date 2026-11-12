from ABH import *
from Resources import *

# 1. نضع دالة مشتركة لتنفيذ أمر الحجرة
async def rock_logic(e):
    target = await to(e)
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    await e.reply(f'اي {await ment(target)}, ({target_id})')

# 2. الهاندلر الأول: مخصص فقط لعبارة "تغيير الحدث"
@ABH.on(events.NewMessage(pattern=r"^تغيير الحدث$"))
async def _(e):
    e.text = 'حجرة @IUHASHEM'
    await e.reply("تم تغيير الحدث")
    await rock_logic(e) # نستدعي الدالة هنا لتعمل فوراً

# 3. الهاندلر الثاني: للأمر الطبيعي
@ABH.on(events.NewMessage(pattern=r"^(?:حجرة|/rock)(?:\s+(.+))?$"))
async def _(e):
    await rock_logic(e)
