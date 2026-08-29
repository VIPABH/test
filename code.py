import asyncio
from telethon import events
from telethon.tl.types import (
    ChannelAdminLogEventActionParticipantToggleAdmin,
    ChannelAdminLogEventActionDefaultBannedRights,
    ChannelParticipantCreator
)

# استيراد العميل المعرف ومُستلم الإشعارات من ملف ABH
from ABH import ABH as client, ALERT_CHAT_ID

@client.on(events.ChatAction())
async def monitor_admin_log(event):
    channel_id = event.chat_id
    
    try:
        # جلب أحدث إجراء في سجل المشرفين
        async for log_entry in client.iter_admin_log(channel_id, limit=1):
            action = log_entry.action
            
            # التحقق من حدث تغيير/ترقية مشرف أو نقل ملكية
            if isinstance(action, ChannelAdminLogEventActionParticipantToggleAdmin):
                new_participant = action.new_participant
                
                # التحقق مما إذا كان المشارك الجديد هو المالك الفعلي (Creator)
                if isinstance(new_participant, ChannelParticipantCreator):
                    new_owner_id = log_entry.user_id
                    admin_who_changed = log_entry.actor_id
                    
                    msg = (
                        f"⚠️ **تنبيه خطير: تم رصد نقل ملكية القناة!**\n\n"
                        f"📢 **معرف القناة:** `{channel_id}`\n"
                        f"👤 **المالك الجديد:** `{new_owner_id}`\n"
                        f"🛠 **بواسطة:** `{admin_who_changed}`"
                    )
                    
                    await client.send_message(ALERT_CHAT_ID, msg)
                    break
                    
    except Exception as e:
        print(f"خطأ أثناء قراءة سجل المشرفين للقناة {channel_id}: {e}")
