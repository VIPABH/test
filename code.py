from ABH import *
from telethon import events, Button

# قاموس حفظ الجلسات
message = {}

# التوجيهات لكل خطوة
arg = {
    'text': 'ارسل الان النص',
    'media': 'ارسل الان الميديا',
    'buttons': 'ارسل الان الزر بالتنسيق الاتي :\nاما اسم الزر بعده : وبعده الرابط\nمثال: `ابن هاشم:https://t.me/wfffp` \nاو ارسل اسم الزر فقط أولاً.'
}

def get_keyboards(user_id):
    """توليد الأزرار ديناميكياً بناءً على بيانات المستخدم الحالية"""
    session = message.get(user_id, {})
    has_text = bool(session.get('text'))
    has_media = bool(session.get('media'))
    has_buttons = bool(session.get('buttons'))

    # استدعاء الألوان وتغيير النصوص بناءً على وجود البيانات
    return [
        [
            Button.inline('إضافة/تعديل النص' if has_text else 'تعيين نص', data='set_text'),
            Button.inline('إضافة/تعديل الميديا' if has_media else 'تعيين ميديا', data='set_media'),
            Button.inline('إضافة/تعديل الزر' if has_buttons else 'تعيين زر', data='set_buttons'),
        ],
        [
            Button.inline('حذف الكل', data='del_all'),
            Button.inline('حذف معين', data='delete'),
        ],
        [
            Button.inline('تم', data='done'),
        ]
    ]

async def send_or_update_preview(e, user_id, notice=None):
    """دالة مركزية لتحديث أو إرسال لوحة التحكم ومعاينة الرسالة"""
    session = message.get(user_id, {})
    text = session.get('text', '')
    media = session.get('media', [])
    buttons = session.get('buttons', [])

    preview = "📋 **معاينة الرسالة الحالية:**\n\n"
    preview += f"📝 **النص:**\n{text if text else 'لا يوجد'}\n\n"
    preview += f"🖼 **عدد الميديا:** {len(media)}\n"
    preview += f"🔘 **عدد الأزرار:** {len(buttons)}\n"

    if notice:
        preview = f"✅ {notice}\n\n" + preview

    keyboards = get_keyboards(user_id)
    
    # إذا كان الاستدعاء من CallbackQuery يتم التعديل، وإلا يتم الإرسال كـ reply
    if hasattr(e, 'edit'):
        await e.edit(preview, buttons=keyboards)
    else:
        await e.respond(preview, buttons=keyboards)

@ABH.on(events.NewMessage(pattern=r'^انشاء رسالة$'))
async def create_message(e):
    user_id = e.sender_id
    message[user_id] = {
        'step': None,
        'text': '',
        'media': [],
        'buttons': [],
        'temp_btn_name': None
    }
    await send_or_update_preview(e, user_id, notice="أهلاً عزيزي، تم فتح جلسة جديدة.")

@ABH.on(events.CallbackQuery(pattern=r'^(set_|del_|delete|done)'))
async def create_message_callback(e):
    data = e.data.decode('utf-8')
    user_id = e.sender_id

    if user_id not in message:
        return await e.edit('جلسة إنشاء الرسالة حذفت، أعد المحاولة.')

    if data == 'del_all':
        del message[user_id]
        return await e.edit('تم حذف الجلسة بنجاح.')

    elif data == 'done':
        message[user_id]['step'] = None
        return await send_or_update_preview(e, user_id, notice="تم إنهاء التعديلات بنجاح!")

    elif data.startswith('set_'):
        step = data.replace('set_', '')
        message[user_id]['step'] = step
        await e.edit(arg.get(step, 'ارسل البيانات المطلوبة:'))

@ABH.on(events.NewMessage)
async def process_inputs(e):
    user_id = e.sender_id

    # التحقق من وجود جلسة وخطوة إدخال تنتظر الرد
    if user_id not in message or not message[user_id].get('step'):
        return

    step = message[user_id]['step']
    text = e.text

    if step == 'text':
        message[user_id]['text'] = text
        message[user_id]['step'] = None
        await send_or_update_preview(e, user_id, notice="تم إضافة/تعديل النص")

    elif step == 'media':
        if e.media:
            message[user_id]['media'].append(e.id)
            message[user_id]['step'] = None
            await send_or_update_preview(e, user_id, notice="تم إضافة الميديا")
        else:
            await e.reply('عذراً عزيزي لازم ترسل ميديا مناسبة.')

    elif step == 'buttons':
        if ':' in text:
            name, url = text.split(':', 1)
            message[user_id]['buttons'].append([name.strip(), url.strip()])
            message[user_id]['step'] = None
            await send_or_update_preview(e, user_id, notice="تم إضافة الزر")
        else:
            message[user_id]['temp_btn_name'] = text
            message[user_id]['step'] = 'button_url'
            await e.reply('تم إضافة اسم الزر، ارسل الرابط الآن:')

    elif step == 'button_url':
        btn_name = message[user_id].pop('temp_btn_name', 'زر')
        message[user_id]['buttons'].append([btn_name, text.strip()])
        message[user_id]['step'] = None
        await send_or_update_preview(e, user_id, notice="تم إضافة رابط الزر")
