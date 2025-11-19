from ABH import *
commands = {}
user_state = {}  # لتخزين الحالة لكل مستخدم

@ABH.on(events.NewMessage)
async def handle_commands(e):
    t = e.text
    uid = e.sender_id

    if uid in user_state:
        state = user_state[uid]
        if state['step'] == 'await_old':
            user_state[uid]['old'] = t
            user_state[uid]['step'] = 'await_new'
            await e.reply('ارسل الامر المختصر')
            return

        elif state['step'] == 'await_new':
            old = state['old']
            new = t
            if new == old:
                await e.reply('الامر المختصر لا يمكن أن يكون نفس الامر الاساسي')
            else:
                commands[old] = new
                await e.reply(f'تم اضافه الامر: {old} -> {new}')
            del user_state[uid]  # إنهاء الحالة
            return
    notf = []
    if t == 'افحص':
        for x in range(385, 491):
            m = await ABH.get_messages('x04ou', ids=x)
            if not m:
                notf.append(x)
        if notf:
            await e.reply("الرسائل المفقودة:\n" + ", ".join(str(n) for n in notf))
        else:
            await e.reply("كل الرسائل موجودة")
    if t == 'ا':
        user_state[uid] = {'step': 'await_old'}
        await e.reply('يجري تغيير الامر, ارسل الامر الاساسي')
    elif t == 'الاوامر':
        if not commands:
            await e.reply('لا توجد اوامر مضافة.')
        else:
            text = "\n".join(f"{old} -> {new}" for old, new in commands.items())
            await e.reply(f"الاوامر الحالية:\n{text}")
