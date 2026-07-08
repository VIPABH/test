from telethon import events, Button
from ABH import ABH 
import math, re

math_session = {}

def get_calc_keyboard(mode="BASIC"):
    if mode == "BASIC":
        return [
            [Button.inline("AC", "AC"), Button.inline("( )", "PAR"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
            [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
            [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
            [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
            [Button.inline("⚙️ ADV", "MODE_ADV"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
        ]
    return [
        [Button.inline("√", "sqrt("), Button.inline("x²", "**2"), Button.inline("+/-", "NEG"), Button.inline("÷", "/")],
        [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
        [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
        [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
        [Button.inline("⬅️ BAS", "MODE_BAS"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
    ]
@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': '', 'mode': 'BASIC', 'par': True}
    await e.reply("🧮 **آلة حاسبة ذكية**", buttons=get_calc_keyboard("BASIC"))

@ABH.on(events.CallbackQuery(pattern=rb'^[0-9+\-*/.=ACDELMOKSG().NPR]+$'))
async def math_callback(e):
    data = e.pattern_match.group(0).decode('utf-8')
    uid = e.sender_id
    
    if uid not in math_session or 'mode' not in math_session[uid]:
        math_session[uid] = {'num': '', 'mode': 'BASIC', 'par': True}
    
    s = math_session[uid]
    
    # التعامل مع تغيير الأوضاع بشكل فوري
    if data == "MODE_ADV": 
        s['mode'] = "ADV"
        await e.edit(text="🧮 **الوضع المتقدم:**", buttons=get_calc_keyboard("ADV"))
        return await e.answer()
        
    elif data == "MODE_BAS": 
        s['mode'] = "BASIC"
        await e.edit(text="🧮 **الوضع الأساسي:**", buttons=get_calc_keyboard("BASIC"))
        return await e.answer()

    # بقية العمليات
    elif data == "AC": s['num'] = ""
    elif data == "DEL": s['num'] = s['num'][:-1]
    elif data == "NEG": 
        try: s['num'] = str(eval(s['num'] or '0') * -1)
        except: pass
    elif data == "PAR":
        s['num'] += "(" if s['par'] else ")"
        s['par'] = not s['par']
    elif data == '=':
        try:
            res = eval(s['num'].replace('sqrt(', 'math.sqrt('), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
            s['num'] = str(int(res) if isinstance(res, float) and res.is_integer() else round(res, 4))
        except: await e.answer("خطأ رياضي", alert=True)
    elif data in ['0','1','2','3','4','5','6','7','8','9','+','-','*','/','.','sqrt(','**2']:
        if data in ['+','-','*','/'] and s['num'] and s['num'][-1] in ['+','-','*','/']:
            s['num'] = s['num'][:-1] + data
        else:
            s['num'] += data

    # تحديث الشاشة للأرقام
    try:
        await e.edit(text=f"🔢 `{s['num'] or '0'}`", buttons=get_calc_keyboard(s['mode']))
    except: pass
    await e.answer()
