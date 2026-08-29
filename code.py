import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ChannelAdminLogEventActionChangeAdmin
from ABH import ABH as client

# استيراد إعدادات الكيان من ملف ABH


@client.on(events.ChatAction())
async def monitor_admin_log(event):
    # استخدام ايدي القناة الذي يأتي من الحدث مباشرة لمراقبة أي قناة يتدخل فيها البوت أو الحساب
    channel_id = event.chat_id
    
    try:
        # جلب أحدث إجراء تم تسجيله في سجل المشرفين للقناة المعنية
        async for log_entry in client.iter_admin_log(channel_id, limit=1):
            action = log_entry.action
            
            # التحقق مما إذا كان الإجراء متعلقاً بتغيير صلاحيات مشرف أو نقل ملكية
            if isinstance(action, ChannelAdminLogEventActionChangeAdmin):
                new_rights = action.new_value
                
                # التحقق إذا ما كانت الصلاحيات الجديدة تتضمن نقل الملكية الكاملة
                if getattr(new_rights, 'is_creator', False):
                    new_owner_id = log_entry.user_id
                    admin_who_changed = log_entry.actor_id
                    
                    msg = (
                        f"⚠️ **تنبيه خطير: تم رصد نقل ملكية القناة!**\n\n"
                        f"📢 **معرف القناة:** `{channel_id}`\n"
                        f"👤 **المشرف الجديد (المالك):** `{new_owner_id}`\n"
                        f"🛠 **بواسطة المشرف:** `{admin_who_changed}`"
                    )
                    
                    # إرسال التنبيه الفوري باستخدام المعرف المستورد من ملف ABH
                    await client.send_message(ALERT_CHAT_ID, msg)
                    break
                    
    except Exception as e:
        print(f"خطأ أثناء قراءة سجل المشرفين للقناة {channel_id}: {e}")
