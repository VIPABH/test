from ABH import *
from Resources import *

@ABH.on(events.NewMessage(pattern=r"^تغيير الحدث$"))
async def _(e):
    e.text = 'حجرة @IUHASHEM'
    await e.reply("تم تغيير الحدث")

# 3. الهاندلر الثاني: للأمر الطبيعي
@ABH.on(events.NewMessage(pattern=r"^(?:حجرة|/rock)(?:\s+(.+))?$"))
async def _(e):
    await e.reply(e.text)
