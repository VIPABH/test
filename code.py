from telethon import events, functions, types
from ABH import *
from telethon import events, functions, types, Button

@ABH.on(events.NewMessage(pattern="^/start$"))
async def _(e):

    await ABH(functions.messages.SendMediaRequest(
        peer=e.sender_id,
        media=types.InputMediaInvoice(
            title="شراء خدمة",
            description="شراء ميزة في البوت",
            invoice=types.Invoice(
                currency="XTR",
                prices=[types.LabeledPrice(label="price", amount=50)]
            ),
            payload=b"buy_service",
            provider_data=types.DataJSON(data="{}")
        ),
        message=""
    ))

    buttons = [
        [Button.user("بروفايل", user_id=e.sender_id)]
    ]
    
    await e.reply("اضغط للدخول للبروفايل:", buttons=buttons)
