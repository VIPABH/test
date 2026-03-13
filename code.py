from telethon.tl.functions.channels import GetParticipantRequest
from telethon import TelegramClient, events, connection, Button
# from shortcut import *
from ABH import *
import asyncio
from telethon import functions, types
from telethon import events, functions, types

@ABH.on(events.NewMessage(pattern="^/start$"))
async def _(e):

    invoice = types.Invoice(
        currency="XTR",
        prices=[types.LabeledPrice(label="price", amount=50)]
    )

    await ABH(functions.messages.SendMediaRequest(
        peer=e.sender_id,
        media=types.InputMediaInvoice(
            title="شراء خدمة",
            description="شراء ميزة في البوت",
            invoice=invoice,
            payload=b"buy_service"
        ),
        message=""
    ))
