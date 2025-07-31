from telethon import events, Button

@ABH.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        'اضغط على الزر لعرض إشعار:',
        buttons=[Button.inline('عرض إشعار', b'show_alert')]
    )

@ABH.on(events.CallbackQuery(data=b'show_alert'))
async def callback(event):
    await event.answer("🚨 هذا هو الإشعار الذي طلبته", alert=True)
