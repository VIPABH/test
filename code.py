from ABH import *
message = {}
@ABH.on(events.NewMessage(pattern=r'^انشاء رسالة$'))
async def create_message(e):
    session = message.get(e.sender_id, {})
    text = session.get('text')
    media = session.get('media')
    buttons = session.get('buttons')
    b = [
        [Button.inline('تعيين نص' if not text else 'اضف او تعديل النص' , data='set_text', icon=5280993797482750213, style= green if not text else blue),
        Button.inline('تعيين ميديا' if not text else 'اضف او تعديل الميديا' , data='set_media', icon=5280993797482750213, style= green if not text else blue),
        Button.inline('تعيين زر' if not text else 'اضف او تعديل الزر' , data='set_url', icon=5280993797482750213, style= green if not text else blue),],
        [
        Button.inline('حذف الكل', data='del_all', icon=5465665476971471368, style=red),
        Button.inline('حذف معين', data='delete', icon=5229113891081956317, style=red),
        ],
        [
        Button.inline('تم', data='done', icon=5854724316385512963, style=green),
        ]
    ]
    await e.reply('اهلا عزيزي وين تحب نبدي', buttons=b)    
