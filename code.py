from ABH import *
commands = {}
user_state = {}
async def x(e):
    await e.reply('hi')
@ABH.on(events.NewMessage)
async def handle_commands(e):
    t = e.text
    uid = e.sender_id
    if t == 'hi':
        await x(e)
        return
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
            del user_state[uid]
            return
    if t == 'ا':
        user_state[uid] = {'step': 'await_old'}
        await e.reply('يجري تغيير الامر, ارسل الامر الاساسي')
    elif t == 'الاوامر':
        if not commands:
            await e.reply('لا توجد اوامر مضافة.')
        else:
            text = "\n".join(f"{old} -> {new}" for old, new in commands.items())
            await e.reply(f"الاوامر الحالية:\n{text}")
