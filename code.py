from ABH import *
@ABH.on(events.NewMessage(pattern=r"^تجربة التنسيق$"))
async def test_direction(event):
    # قائمة تحتوي على كلمات عربية وانجليزية وآيديات
    test_list = ["سيف", "Gemini", "12345", "بوت الحماية", "Python_Code"]
    
    # 1. النص بدون حماية (سينعكس إذا بدأ بكلمة إنجليزية)
    msg_normal = "❌ **بدون تنسيق (عشوائي):**\n"
    for i, item in enumerate(test_list, start=1):
        msg_normal += f"{i} - `{item}`\n"
    
    # 2. النص مع حماية RLM (سيبقى من اليمين دائماً)
    RLM = "\u200f" # رمز Right-to-Left Mark
    msg_fixed = f"{RLM}✅ **مع تنسيق (محاذاة لليمين):**\n"
    for i, item in enumerate(test_list, start=1):
        msg_fixed += f"{RLM}{i} - `{item}`\n"
    
    # إرسال التجربتين في رسالة واحدة للمقارنة
    final_report = msg_normal + "\n" + "—" * 15 + "\n\n" + msg_fixed
    await event.reply(final_report)
