from telethon import events, types, functions
from ABH import ABH as client

@client.on(events.NewMessage)
async def auto_promote(event):
    # تجاهل الرسائل الخاصة
    if not (event.is_group or event.is_channel):
        return

    try:
        user = await event.get_sender()
        chat = await event.get_chat()

        # إعداد صلاحيات فارغة (بدون أي صلاحيات)
        rights = types.ChatAdminRights(
            change_info=False,
            post_messages=False,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            anonymous=False,
            manage_call=False,
            other=False
        )

        # لقب المشرف
        rank_title = "مشرف ثانوي"

        # تنفيذ الترقية
        if isinstance(chat, types.Channel):
            # القنوات والسوبر كروبات
            await client(functions.channels.EditAdminRequest(
                channel=chat,
                user_id=user.id,
                admin_rights=rights,
                rank=rank_title
            ))
        else:
            # المجموعات العادية (basic group)
            await client(functions.messages.EditChatAdminRequest(
                chat_id=chat.id,
                user_id=user.id,
                is_admin=True
            ))

        print(f"✅ تم رفع {user.first_name} في {chat.title} كلقب '{rank_title}' بدون صلاحيات.")

    except Exception as e:
        print(f"⚠️ خطأ أثناء رفع المستخدم: {e}")