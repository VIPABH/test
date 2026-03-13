from telethon import events, functions, types
from ABH import *
from telethon import events, functions, types

@ABH.on(events.NewMessage(pattern="^/start$"))
async def _(e):

    await ABH(functions.messages.SendInvoiceRequest(
        peer=e.sender_id,
        title="شراء خدمة",
        description="شراء ميزة في البوت",
        currency="XTR",
        prices=[
            types.LabeledPrice(label="price", amount=50)
        ],
        payload=b"buy_service",
        provider_token="",   # فارغ عند استخدام XTR
        start_param="start"
    ))
