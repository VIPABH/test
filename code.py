from telethon import events, Button
from ABH import ABH 
math_session = {}
def get_buttons():
    return [
        [Button.inline("AC", data="AC"), Button.inline("C", data="C"), Button.inline("÷", data="/")],
        [Button.inline("7", data="7"), Button.inline("8", data="8"), Button.inline("9", data="9"), Button.inline("*", data="*")],
        [Button.inline("4", data="4"), Button.inline("5", data="5"), Button.inline("6", data="6"), Button.inline("-", data="-")],
        [Button.inline("1", data="1"), Button.inline("2", data="2"), Button.inline("3", data="3"), Button.inline("+", data="+")],
        [Button.inline("0", data="0"), Button.inline(".", data="."), Button.inline("=", data="=")]
    ]
@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': ''}
    await e.reply("أهلاً بك في الحاسبة العلمية.\nابدأ بإدخال الأرقام:", buttons=get_buttons())
@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=AC]+$'))
async def math_callback(e):
    if e.sender_id not in math_session:
        return await e.answer("يرجى كتابة 'الحاسبة' أولاً 🙃")
    data = e.pattern_match.group(0).decode('utf-8')
    current_eq = math_session[e.sender_id].get('num', '')
    if data == "AC":
        math_session[e.sender_id]['num'] = ""
        await e.edit(text="تم تصفير الجلسة:", buttons=get_buttons())
    elif data == "C":
        await e.edit(text=f"تم حذف ( {current_eq[-1]} ):\n{math_session[e.sender_id]['num']}", buttons=get_buttons())        
        math_session[e.sender_id]['num'] = current_eq[:-1]
    elif data.isdigit() or data == '.':
        math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة:\n{math_session[e.sender_id]['num']}", buttons=get_buttons())        
    elif data in ['+', '-', '*', '/']:
        if current_eq and current_eq[-1] in ['+', '-', '*', '/']:
            math_session[e.sender_id]['num'] = current_eq[:-1] + data
        else:
            math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة:\n{math_session[e.sender_id]['num']}", buttons=get_buttons())        
    elif data == '=':
        try:
            الناتج = eval(current_eq)
            math_session[e.sender_id]['num'] = str(الناتج)
            await e.edit(text=f"{الناتج=}", buttons=get_buttons())
        except Exception:
            await e.answer("معادلة خاطئة!")
    await e.answer()
