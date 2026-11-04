from ABH import ABH 
from telethon import events
from telethon.tl.types import InputKeyboardButtonUserProfile, InputUser
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow

# افترض أنك مسجل الأحداث هكذا مع ABH (وهو مثيل Telethon Client)
@ABH.on(events.NewMessage(pattern='/profile_btn'))
async def send_profile_button(event):
    # الحصول على معلومات المرسل أو استخدام دالة الـ button_mention التي عدلناها سابقاً
    sender = await event.get_sender()
    
    if not sender:
        return

    # إنشاء زر الملف الشخصي
    input_user = await ABH.get_input_user(sender)
    profile_button = InputKeyboardButtonUserProfile(
        text=f"ملف {getattr(sender, 'first_name', 'المستخدم')}",
        user_id=input_user
    )
    
    # وضع الزر داخل لوحة مفاتيح (ReplyKeyboardMarkup أو InlineKeyboardMarkup حسب الاستخدام)
    # ملاحظة: أزرار الملف الشخصي عادةً تُوضع في ReplyKeyboardMarkup أو Inline حسب إصدار تيليثون
    markup = ReplyKeyboardMarkup(
        rows=[KeyboardButtonRow(buttons=[profile_button])],
        resize=True
    )
    
    # إرسال الرسالة مع الزر
    await event.reply("اضغط على الزر أدناه لعرض الملف الشخصي:", buttons=markup)
