# monitor_restrictions.py
# ملاحظة: غيّر API_ID و API_HASH و SESSION قبل التشغيل
import asyncio
from telethon import TelegramClient, events
from ABH import ABH as client

# ترجع معرف الحساب الذي يشغّل هذا السكربت
async def my_id():
    me = await client.get_me()
    return me.id

# 1) رصد فوري عبر ChatAction (banned_rights, new_admin_rights, kicked_by)
@client.on(events.ChatAction)
async def chat_action(evt):
    # مثال: evt.chat_id, evt.user_id, evt.kicked_by, evt.banned_rights, evt.new_admin_rights
    if getattr(evt, "banned_rights", None):
        # حدث تقييد/حظر
        actor = getattr(evt, "kicked_by", None) or getattr(evt, "added_by", None) or None
        print("تقييد", "subject=", getattr(evt, "user_id", None), "by=", actor)
    elif getattr(evt, "kicked_by", None):
        # طرد مباشر
        print("طرد", "subject=", getattr(evt, "user_id", None), "by=", evt.kicked_by)
    elif getattr(evt, "new_admin_rights", None):
        # رفع إلى مشرف
        print("رفع", "subject=", getattr(evt, "user_id", None), "by=", getattr(evt, "added_by", None) or None)

# 2) فحص سجل الإدارة للحصول على أحداث مفصّلة (أفضل لتحديد actor_id وaction type)
async def admin_log_watcher():
    async for dialog in client.iter_dialogs():
        if not (dialog.is_group or dialog.is_channel):
            continue
        chat = dialog.id
        # نحصل على آخر N أحداث إدارية (تستطيع تخزين معرفات لمعالجة فقط الجديد لاحقًا)
        async for entry in client.iter_admin_log(entity=chat, limit=200):
            try:
                action_name = type(entry.action).__name__ if entry.action else ""
                subject = getattr(entry, "user_id", None) or getattr(entry, "user_ids", None)
                actor = getattr(entry, "actor_id", None)
                # أشياء محتملة بالاسم:
                if "Ban" in action_name or "Kick" in action_name or "EditBanned" in action_name:
                    print("تقييد/طرد (adminlog):", action_name, "subject=", subject, "by=", actor)
                elif "Promote" in action_name or "EditAdmin" in action_name:
                    print("رفع (adminlog):", action_name, "subject=", subject, "by=", actor)
            except Exception:
                continue
        # لا نريد أن نعيد فحص نفس الديالوغ بلا توقف -> يمكن الانتظار
    # نخلي الدالة تعمل على فواصل زمنية
    await asyncio.sleep(10)
    # وفي الاستخدام الحقيقي نكرر الحلقة أو ندمج منطق تذكّر آخر حدث
