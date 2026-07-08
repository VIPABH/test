from telethon import events, Button
from ABH import ABH 
import math

math_session = {}

def get_calc_keyboard():
    return [
        [Button.inline("AC", "AC"), Button.inline("( )", "PAR"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
        [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
        [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
        [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
        [Button.inline("+/-", "NEG"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
    ]

@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': '', 'par': True}
    await e.reply("🧮 **الحاسبة:**", buttons=get_calc_keyboard())

@ABH.on(events.CallbackQuery(pattern=rb'^[0-9+\-*/.=ACDELNP]+$'))
async def math_callback(e):
    data = e.pattern_match.group(0).decode('utf-8')
    uid = e.sender_id
    
    if uid not in math_session:
        math_session[uid] = {'num': '', 'par': True}
    
    s = math_session[uid]
    
    if data == "AC": s['num'] = ""
    elif data == "DEL": s['num'] = s['num'][:-1]
    elif data == "NEG": 
        try: s['num'] = str(eval(s['num'] or '0') * -1)
        except: pass
    elif data == "PAR":
        s['num'] += "(" if s['par'] else ")"
        s['par'] = not s['par']
    elif data == '=':
        try:
            res = eval(s['num'], {"__builtins__": None})
            s['num'] = str(int(res) if isinstance(res, float) and res.is_integer() else round(res, 4))
        except: await e.answer("خطأ", alert=True)
    elif data in ['0','1','2','3','4','5','6','7','8','9','+','-','*','/','.']:
        if data in ['+','-','*','/'] and s['num'] and s['num'][-1] in ['+','-','*','/']:
            s['num'] = s['num'][:-1] + data
        else:
            s['num'] += data

    try:
        await e.edit(text=f"🔢 `{s['num'] or '0'}`", buttons=get_calc_keyboard())
    except: pass
    await e.answer()
