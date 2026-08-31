from ABH import *
from telethon.tl.custom import Button

@ABH.on(events.NewMessage)
async def _(e):
    # جلب الـ InputEntity الخاص بالمرسل لتمريره لـ Button.mention
    user_entity = await ABH.get_input_entity(e.sender_id)
    
    # إرسال الرسالة مع زر المنشن
    await e.reply('>', buttons=[
        [Button.mention('--', user_entity)]
    ])
