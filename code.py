from telethon import events, types
from telethon.tl.custom import Button
from ABH import *

def mention_button(text, user_entity):
    # تحويل الـ InputEntity إلى InputUser يتضمن access_hash
    input_user = types.InputUser(
        user_id=user_entity.user_id,
        access_hash=user_entity.access_hash
    )
    return types.KeyboardButtonRow(
        buttons=[types.InputKeyboardButtonUserProfile(text=text, user_id=input_user)]
    )

Button.mention = staticmethod(mention_button)

@ABH.on(events.NewMessage)
async def _(e):
    # جلب entity المستخدم المرسل
    user_entity = await ABH.get_input_entity(e.sender_id)
    
    # إرسال الزر المغلف
    await e.reply('>', buttons=[
        [Button.mention('--', user_entity)]
    ])
