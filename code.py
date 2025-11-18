from ABH import *
commands = {}
@ABH.on(events.NewMessage)
async def handle_commands(e):
    t = e.text
    if t == 'ا':
        await e.reply('يجري تغيير الامر, ارسل الامر الاساسي')
        o = (await ABH.wait_for(events.NewMessage(from_users=e.sender_id))).text
        await e.reply('ارسل الامر المختصر')
        n = (await ABH.wait_for(events.NewMessage(from_users=e.sender_id))).text
        if n == o:
            await e.reply('الامر المختصر لا يمكن أن يكون نفس الامر الاساسي')
            return
        commands[o] = n
        await e.reply(f'تم اضافه الامر: {o} -> {n}')
    elif t == 'الاوامر':
        if not commands:
            await e.reply('لا توجد اوامر مضافة.')
        else:
            text = "\n".join(f"{old} -> {new}" for old, new in commands.items())
            await e.reply(f"الاوامر الحالية:\n{text}")
