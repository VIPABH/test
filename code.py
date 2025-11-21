from ABH import *
from telethon import events

# تخزين آخر media group تمت معالجته
processed_groups = set()

@ABH.on(events.NewMessage)
async def handle_commands(e):
    # إذا توجد وسائط
    if e.media:
        # إذا الرسالة جزء من media group
        gid = getattr(e, 'grouped_id', None)

        if gid:
            # إذا سبق الرد على هذا الـ group → لا تكرر الرد
            if gid in processed_groups:
                return
            processed_groups.add(gid)

        # ردّ واحد فقط
        return await e.reply('x')
