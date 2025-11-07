from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH as bot

print(" >>")  # أول خطوة
@bot.on(events.ChatAction)
async def monitor_admin(event):
    print("📢 حدث جديد تم التقاطه")  # أول خطوة

    me = await bot.get_me()
    print(f"✅ تم الحصول على بيانات البوت: {me.id}")

    # نتحقق فقط إذا هناك تغيير في صلاحيات المشرفين
    if getattr(event, "new_admin_rights", None):
        print("⚙️ تم اكتشاف تغيير في صلاحيات المشرفين")

        try:
            perms = await bot.get_permissions(event.chat_id, me.id)
            print(f"🔍 تم جلب صلاحيات البوت: {perms}")

            if perms.is_admin:
                print("✅ البوت مشرف حالياً")
                try:
                    await event.reply("تم رفع البوت إلى مشرف ✅")
                    print("📩 تم إرسال رسالة تأكيد")
                except Exception as e:
                    print(f"⚠️ فشل إرسال الرسالة: {e}")

            else:
                print("❌ تم تنزيل البوت من الإشراف")
                try:
                    await event.reply("تم تنزيل البوت من الاشراف! سأخرج ❌")
                    print("📩 تم إرسال رسالة قبل الخروج")
                except Exception as e:
                    print(f"⚠️ فشل إرسال الرسالة: {e}")

                try:
                    await bot(LeaveChannelRequest(event.chat_id))
                    print("🚪 البوت خرج من المجموعة بنجاح")
                except Exception as e:
                    print(f"💥 فشل الخروج من المجموعة: {e}")

        except Exception as e:
            print(f"💢 خطأ أثناء التحقق من الصلاحيات: {e}")
            try:
                await bot(LeaveChannelRequest(event.chat_id))
                print("🚪 تم الخروج بسبب خطأ في التحقق")
            except Exception as e2:
                print(f"💥 فشل الخروج بعد الخطأ: {e2}")
    else:
        print("⏭️ الحدث لا يحتوي على new_admin_rights — تم تجاهله")
