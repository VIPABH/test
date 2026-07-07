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
    
    # 1. التصفير (AC)
    if data == "AC":
        math_session[e.sender_id]['num'] = ""
        await e.edit(text="تم تصفير الجلسة", buttons=get_buttons())
        
    # 2. الحذف (C)
    elif data == "C":
        new_eq = current_eq[:-1]
        math_session[e.sender_id]['num'] = new_eq
        await e.edit(text=f"المعادلة:\n{new_eq}", buttons=get_buttons())
        
    # 3. الأرقام والنقطة
    elif data.isdigit() or data == '.':
        math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة:\n{math_session[e.sender_id]['num']}", buttons=get_buttons())
        
    # 4. العمليات (+, -, *, /)
    elif data in ['+', '-', '*', '/']:
        # المنطق المطلوب: إذا تم إدخال عمليتين متتاليتين، نستبدل الأخيرة
        if current_eq and current_eq[-1] in ['+', '-', '*', '/']:
            math_session[e.sender_id]['num'] = current_eq[:-1] + data
        else:
            math_session[e.sender_id]['num'] = current_eq + data
        await e.edit(text=f"المعادلة:\n{math_session[e.sender_id]['num']}", buttons=get_buttons())
        
    # 5. الحساب (=)
    elif data == '=':
        try:
            # تنظيف المعادلة من العمليات المتكررة غير المنطقية قبل الحساب
            # مثال: تحويل ++ إلى + أو +- إلى -
            result = eval(current_eq)
            # تحديث الجلسة بالناتج ليتمكن المستخدم من إكمال الحساب عليه
            math_session[e.sender_id]['num'] = str(result)
            await e.edit(text=f"الناتج:\n{current_eq} = {result}", buttons=get_buttons())
        except Exception:
            await e.answer("معادلة خاطئة!", alert=True)
            
    await e.answer()
