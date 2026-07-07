from telethon import Button
from ABH import *
math_session = {}
button = [
    [
        Button.inline("7", data="7"),
        Button.inline("8", data="8"),
        Button.inline("9", data="9"),
        Button.inline("/", data="/")
    ],
    [
        Button.inline("4", data="4"),
        Button.inline("5", data="5"),
        Button.inline("6", data="6"),
        Button.inline("*", data="*")
    ],
    [
        Button.inline("1", data="1"),
        Button.inline("2", data="2"),
        Button.inline("3", data="3"),
        Button.inline("-", data="-")
    ],
    [
        Button.inline("0", data="0"),
        Button.inline(".", data="."),
        Button.inline("=", data="="),
        Button.inline("+", data="+")
    ]
]
@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def math(e):
    math_session.setdefault(e.sender_id, {})
    await e.reply("الحاسبة العلمية شغاله, ادخل معادلتك", buttons=button)
