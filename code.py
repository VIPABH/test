from telethon.tl.types import InputPeerUser
from telethon import events
from ABH import ABH
import os

@ABH.on(events.NewMessage(pattern='^(صورتي|صورة البروفايل)$'))
async def mypic(event):
    try:
        # الحصول على معلومات المرسل مع معالجة الأخطاء
        sender = await event.get_sender()
        
        # جلب البيانات الكاملة للمستخدم (مهم للوصول إلى البايو)
        try:
            full_user = await event.client.get_entity(sender.id)
        except ValueError:
            await event.reply("❌ لا يمكن الوصول إلى معلومات الملف الشخصي")
            return

        # تحميل الصورة بجودة عالية مع ضغط
        photo_path = f"temp_profile_{sender.id}.jpg"
        try:
            photo = await event.client.download_profile_photo(
                full_user,
                file=photo_path,
                download_big=True  # لتحميل أعلى جودة
            )
        except Exception as download_error:
            await event.reply("⚠️ فشل في تحميل الصورة")
            return

        if photo:
            # معالجة البايو مع تنسيق متقدم
            bio = getattr(full_user, 'about', None)
            if bio:
                formatted_bio = f"""
                📝 **الوصف الشخصي**:
                `{bio}`
                """
            else:
                formatted_bio = "`لا يوجد وصف في الملف الشخصي`"

            # إرسال الصورة مع البايو
            try:
                await event.client.send_file(
                    event.chat_id,
                    file=photo,
                    caption=formatted_bio,
                    reply_to=event.id,
                    parse_mode='markdown',
                    allow_cache=False,
                    attributes=[DocumentAttributeFilename(f"profile_{sender.id}.jpg")]
                )
            except Exception as send_error:
                await event.reply(f"⚠️ فشل في إرسال الصورة: {str(send_error)}")

            # تنظيف الملفات المؤقتة
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except:
                pass
        else:
            await event.reply("⚠️ لم يتم العثور على صورة بروفايل", reply_to=event.id)

    except Exception as main_error:
        await event.reply(f"❌ خطأ غير متوقع: {str(main_error)}")
        # تنظيف الملفات في حالة الخطأ
        if 'photo_path' in locals() and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass
