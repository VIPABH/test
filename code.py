from telethon import events
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    InputKeyboardButtonUserProfile,
    InputUser,
)
from ABH import ABH

async def button_mention(e, id=None, text=None):
    # 1. استخدام المعرف الممرر id أو المعرف الافتراضي إذا لم يتم تمريره
    target_user_id = id if id else 1910015590
    
    # 2. جلب كائن المستخدم الكامل (User) للحصول على first_name وكائن InputEntity
    user_entity = await ABH.get_entity(target_user_id)
    input_peer = await ABH.get_input_entity(user_entity)
    
    # 3. جلب النص من اسم المستخدم (first_name) إذا لم يتم تمرير text
    button_text = text if text else getattr(user_entity, 'first_name', 'User')
    
    # 4. إنشاء كائن InputUser
    user_input = InputUser(user_id=input_peer.user_id, access_hash=input_peer.access_hash)
    
    # 5. بناء الـ Inline Markup
    markup = ReplyInlineMarkup(
        rows=[
            KeyboardButtonRow(
                buttons=[
                    InputKeyboardButtonUserProfile(
                        text=button_text,
                        user_id=user_input
                    )
                ]
            )
        ]
    )
    return markup
