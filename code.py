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
    await e.reply("🔢 **الحاسبة العلمية جاهزة**\n\nأدخل معادلتك:", buttons=get_buttons())

@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=AC]+$'))
async def math_callback(e):
    if e.sender_id not in math_session:
        return await e.answer("يرجى كتابة 'الحاسبة' أولاً 🙃")
    
    data = e.pattern_match.group(0).decode('utf-8')
    current_eq = math_session[e.sender_id].get('num', '')
    
    # 1. تصفير
    if data == "AC":
        math_session[e.sender_id]['num'] = ""
        await e.edit(text="🔢 **تم التصفير، ابدأ من جديد:**", buttons=get_buttons())
        
    # 2. حذف خانة
    elif data == "C":
        new_val = current_eq[:-1]
        math_session[e.sender_id]['num'] = new_val
        await e.edit(text=f"🔢 **المعادلة:**\n`{new_val}`", buttons=get_buttons())
        
    # 3. أرقام ونقطة
    elif data.isdigit() or data == '.':
        math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"🔢 **المعادلة:**\n`{math_session[e.sender_id]['num']}`", buttons=get_buttons())
        
    # 4. عمليات حسابية
    elif data in ['+', '-', '*', '/']:
        if current_eq and current_eq[-1] in ['+', '-', '*', '/']:
            math_session[e.sender_id]['num'] = current_eq[:-1] + data
        else:
            math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"🔢 **المعادلة:**\n`{math_session[e.sender_id]['num']}`", buttons=get_buttons())
        
    # 5. حساب النتيجة
    elif data == '=':
        eq = current_eq
        # تصحيح الإشارات النهائية
        if eq.endswith('-'): eq = '-' + eq[:-1]
        elif eq.endswith('+'): eq = eq[:-1]
            
        try:
            result = eval(eq)
            # تنسيق الناتج بفاصلة للأرقام الكبيرة (إذا كان رقم)
            formatted_result = f"{result:,.2f}" if isinstance(result, (int, float)) else result
            
            await e.edit(text=f"✅ **الناتج:**\n`{eq} = {formatted_result}`", buttons=get_buttons())
            math_session[e.sender_id]['num'] = str(result)
        except ZeroDivisionError:
            await e.answer("خطأ: لا يمكن القسمة على صفر!", alert=True)
        except Exception:
            await e.answer("معادلة خاطئة!", alert=True)
            
    await e.answer()
