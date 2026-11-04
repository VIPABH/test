from telethon import events
from telethon.tl import *  # استيراد كل شيء لمنع ظهور أي NameError أو ImportError
from ABH import ABH

@ABH.on(events.NewMessage(pattern=r'\.زر'))
async def button_mention(e):
    if not e.sender_id:
        return
        
    text = '>>'
    
    # الحصول على الكيان والـ InputUser بأمان
    input_peer = await ABH.get_input_entity(e.sender_id)
    
    if not hasattr(input_peer, 'user_id'):
        return

    user_input = types.InputUser(user_id=input_peer.user_id, access_hash=input_peer.access_hash)  
    
    # ملاحظة: إذا كنت تستخدم الكلاس القديم للأزرار، تأكد من استخدامه هكذا:
    # (إذا استمرت مشكلة InputKeyboardButtonUserProfile، يفضل استخدام Button.url كما شرحنا سابقاً)
    
    # بناء الكيبورد باستخدام الأنواع المستوردة
    markup = types.ReplyInlineMarkup(
        rows=[
            types.KeyboardButtonRow(
                buttons=[
                    types.KeyboardButtonUrl(
                        text=text,
                        url=f"tg://user?id={e.sender_id}"
                    )
                ]
            )
        ]
    )
    
    await e.reply('[]', buttons=markup)
    return markup
