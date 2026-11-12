from ABH import *
from Resources import *
@ABH.on(events.NewMessage)
async def _(e):
    text = e.text
    if text == 'تغيير الحدث':
        e.text = 'حجرة @IUHASHEM'
        await e.reply("تم تغيير الحدث")
    else:
        await e.reply('حدث عادي')
@ABH.on(events.NewMessage(pattern=r"^(?:حجرة|/rock)(?:\s+(.+))?$"))
async def _(e):
    target = await to(e)
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    await e.reply(f'اي {await ment(target)}, ({targte_id})')
