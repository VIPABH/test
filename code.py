from telethon import events, Button
from ABH import ABH 
import math

math_session = {}

def get_calc_keyboard(current_text=""):
    """دالة لإنشاء لوحة مفاتيح الحاسبة بشكل مرتب"""
    buttons = [
        [Button.inline("AC", "AC"), Button.inline("C", "C"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
        [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
        [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
        [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
        [Button.inline("+/-", "NEG"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
    ]
    return buttons

@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': ''}
    await e.reply("🧮 **آلة حاسبة ذكية**\n\nأدخل الأرقام للبدء:", buttons=get_calc_keyboard())

@ABH.on(events.CallbackQuery(pattern=b'^[0-9+\-*/.=ACDELNEG]+$'))
async def math_callback(e):
    uid = e.sender_id
    if uid not in math_session: return await e.answer("انتهت الجلسة، اكتب 'الحاسبة' مجدداً")
    
    data = e.pattern_match.group(0).decode('utf-8')
    eq = math_session[uid].get('num', '')
    
    # معالجة الأزرار
    if data == "AC":
        eq = ""
    elif data == "DEL":
        eq = eq[:-1]
    elif data == "NEG":
        # قلب إشارة آخر رقم
        if eq: eq = str(eval(eq) * -1)
    elif data.isdigit() or data == '.':
        eq += data
    elif data in ['+', '-', '*', '/']:
        if eq and eq[-1] in ['+', '-', '*', '/']: eq = eq[:-1] + data
        else: eq += data
    elif data == '=':
        try:
            res = eval(eq)
            eq = str(int(res) if isinstance(res, float) and res.is_integer() else res)
        except:
            await e.answer("خطأ رياضي!", alert=True)
    
    math_session[uid]['num'] = eq
    
    # عرض النتيجة بتنسيق مرتب
    display_text = f"🔢 **المعادلة:**\n`{eq if eq else '0'}`"
    if data == '=':
        display_text = f"✅ **الناتج النهائي:**\n`{str(eq):,}`"
        
    await e.edit(text=display_text, buttons=get_calc_keyboard(eq))
    await e.answer()
