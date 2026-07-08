from telethon import events, Button
from ABH import ABH 
math_session = {}
def get_calc_keyboard():
    return [
        [Button.inline("AC", "AC"), Button.inline("( )", "C"), Button.inline("⌫", "DEL"), Button.inline("÷", "/")],
        [Button.inline("7", "7"), Button.inline("8", "8"), Button.inline("9", "9"), Button.inline("×", "*")],
        [Button.inline("4", "4"), Button.inline("5", "5"), Button.inline("6", "6"), Button.inline("-", "-")],
        [Button.inline("1", "1"), Button.inline("2", "2"), Button.inline("3", "3"), Button.inline("+", "+")],
        [Button.inline("+/-", "NEG"), Button.inline("0", "0"), Button.inline(".", "."), Button.inline("=", "=")]
    ]
@ABH.on(events.NewMessage(pattern="الحاسبة"))
async def start_math(e):
    math_session[e.sender_id] = {'num': '', 'par': True}
    await e.reply("🧮 **آلة حاسبة ذكية**", buttons=get_calc_keyboard())
@ABH.on(events.CallbackQuery(pattern=rb'^[0-9+\-*/.=ACDELNEG]+$'))
async def math_callback(e):
    uid = e.sender_id
    if uid not in math_session: return await e.answer("اكتب 'الحاسبة' مجدداً")    
    data = e.pattern_match.group(0).decode('utf-8')
    s = math_session[uid]
    eq = s['num']
    if data == "AC":
        eq = ""
    elif data == "DEL":
        eq = eq[:-1]
    elif data == "C": 
        eq += "(" if s['par'] else ")"
        s['par'] = not s['par']
    elif data == "NEG":
        if eq: 
            try: eq = str(eval(eq) * -1)
            except: pass
    elif data.isdigit() or data == '.':
        eq += data
    elif data in ['+', '-', '*', '/']:
        if eq and eq[-1] in ['+', '-', '*', '/']: eq = eq[:-1] + data
        else: eq += data
    elif data == '=':
        try:
            res = eval(eq)
            eq = str(int(res) if isinstance(res, (int, float)) and (float(res)).is_integer() else res)
        except:
            await e.answer("خطأ رياضي!")
    s['num'] = eq    
    display_text = f"🔢 **المعادلة:**\n`{eq if eq else '0'}`"
    await e.edit(text=display_text, buttons=get_calc_keyboard())
    await e.answer()
