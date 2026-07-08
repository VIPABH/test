from telethon import events, Button
from ABH import ABH 
import math
import re

# قاموس لتخزين حالة كل مستخدم (المعادلة + الوضع الحالي)
math_session = {}

def get_calc_keyboard(mode="BASIC"):
    """إنشاء لوحة المفاتيح بناءً على الوضع المختار"""
    if mode == "BASIC":
        return [
            [Button.inline("AC", "AC"), Button.inline("C", "C"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
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
    """تنسيق الأرقام داخل المعادلة بفواصل للقراءة السهلة"""
    return re.sub(r'(\d+)', lambda m: f"{int(m.group(1)):,}", eq)

@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': '', 'mode': 'BASIC'}
    await e.reply("🧮 **آلة حاسبة ذكية**\n\nأدخل الأرقام للبدء:", buttons=get_calc_keyboard("BASIC"))

@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=ACDELMOKSG().]+$'))
async def math_callback(e):
    uid = e.sender_id
    if uid not in math_session: 
        return await e.answer("انتهت الجلسة، اكتب 'الحاسبة' مجدداً")
    
    data = e.pattern_match.group(0).decode('utf-8')
    session = math_session[uid]
    eq = session['num']
    
    # 1. التبديل بين الأوضاع
    if data == "MODE_ADV": session['mode'] = "ADV"
    elif data == "MODE_BAS": session['mode'] = "BASIC"
    
    # 2. العمليات الأساسية
    elif data == "AC": session['num'] = ""
    elif data == "DEL": session['num'] = eq[:-1]
    
    # 3. الحساب (=)
    elif data == '=':
        try:
            # تهيئة المعادلة للعمليات المتقدمة
            calc_eq = eq.replace('sqrt(', 'math.sqrt(')
            res = eval(calc_eq, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
            
            # تنسيق الناتج: بدون أصفار إذا كان صحيحاً
            if isinstance(res, float) and res.is_integer(): res = int(res)
            session['num'] = str(res)
        except ZeroDivisionError: await e.answer("خطأ: لا يمكن القسمة على صفر!", alert=True)
        except Exception: await e.answer("معادلة خاطئة!", alert=True)
    
    # 4. إضافة الأرقام والرموز
    elif data in ['0','1','2','3','4','5','6','7','8','9','+','-','*','/','(',')','.','sqrt(']:
        # منع تكرار العمليات
        if data in ['+','-','*','/'] and eq and eq[-1] in ['+','-','*','/']:
            session['num'] = eq[:-1] + data
        else:
            session['num'] += data

    # تحديث واجهة الرسالة
    new_eq = session['num']
    display = f"🔢 **المعادلة:**\n`{format_eq(new_eq) if new_eq else '0'}`"
    if data == '=':
        display = f"✅ **الناتج:**\n`{new_eq}`"
    
    await e.edit(text=display, buttons=get_calc_keyboard(session['mode']))
    await e.answer()
