from telethon import events, Button
from ABH import ABH 
import math
import re

# قاموس لتخزين حالة كل مستخدم
math_session = {}

def get_calc_keyboard(mode="BASIC"):
    """إنشاء لوحة المفاتيح مع التعديلات الجديدة"""
    if mode == "BASIC":
        return [
            [Button.inline("AC", "AC"), Button.inline("±", "C"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
            [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
            [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
            [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
            [Button.inline("⚙️ ADV", "MODE_ADV"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
        ]
    else: # الوضع المتقدم
        return [
            [Button.inline("√", "sqrt("), Button.inline("x²", "**2"), Button.inline("(", "("), Button.inline(")", ")")],
            [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("÷", "/")],
            [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("×", "*")],
            [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("-", "-")],
            [Button.inline("⬅️ BAS", "MODE_BAS"), Button.inline("0", "0"), Button.inline("+", "+"), Button.inline("=", "=")]
        ]

def format_eq(eq):
    return re.sub(r'(\d+)', lambda m: f"{int(m.group(1)):,}", eq)

@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': '', 'mode': 'BASIC'}
    await e.reply("🧮 **الحاسبة الذكية:**", buttons=get_calc_keyboard("BASIC"))

@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=ACDELMOKSG().]+$'))
async def math_callback(e):
    uid = e.sender_id
    if uid not in math_session: return await e.answer("اكتب 'الحاسبة' أولاً")
    
    data = e.pattern_match.group(0).decode('utf-8')
    session = math_session[uid]
    
    if data == "MODE_ADV": session['mode'] = "ADV"
    elif data == "MODE_BAS": session['mode'] = "BASIC"
    elif data == "AC": session['num'] = ""
    elif data == "DEL": session['num'] = session['num'][:-1]
    
    # زر C للتحويل بين الموجب والسالب
    elif data == "C":
        if session['num']:
            try:
                # قلب إشارة الرقم الأخير أو ناتج العملية
                val = eval(session['num'])
                session['num'] = str(val * -1)
            except: pass
            
    elif data == '=':
        try:
            calc_eq = session['num'].replace('sqrt(', 'math.sqrt(')
            res = eval(calc_eq, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
            if isinstance(res, float) and res.is_integer(): res = int(res)
            session['num'] = str(res)
        except: await e.answer("خطأ!", alert=True)
    
    elif data in ['0','1','2','3','4','5','6','7','8','9','+','-','*','/','(',')','.','sqrt(','**2']:
        if data in ['+','-','*','/'] and session['num'] and session['num'][-1] in ['+','-','*','/']:
            session['num'] = session['num'][:-1] + data
        else:
            session['num'] += data

    eq = session['num']
    display = f"🔢 **المعادلة:**\n`{format_eq(eq) if eq else '0'}`"
    if data == '=': display = f"✅ **الناتج:**\n`{eq}`"
    
    await e.edit(text=display, buttons=get_calc_keyboard(session['mode']))
    await e.answer()
