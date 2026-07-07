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
@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=]$'))
async def math_callback(e):
    if not (e.sender_id in math_session):
        return await e.answer("🙃")
    data = e.pattern_match.group(0).decode('utf-8')
    if data.isdigit() or data == '.':
        current_eq = math_session[e.sender_id].get('num', '')
        math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة: {math_session[e.sender_id]['num']}", buttons=button)        
    elif data in ['+', '-', '*', '/']:
        current_eq = math_session[e.sender_id].get('num', '')
        math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة: {math_session[e.sender_id]['num']}", buttons=button)
    elif data == '=':
        current_eq = math_session[e.sender_id].get('num', '0')
        try:
            result = eval(current_eq)
            await e.edit(text=f"النتيجة: {current_eq} = {result}", buttons=button)
            math_session[e.sender_id]['num'] = str(result)
        except Exception:
            await e.answer("خطأ في المعادلة!", alert=True)
    await e.answer()
