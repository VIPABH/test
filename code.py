"""
بوت تلكرام عادي (Bot Token) للتحكم في المكالمة الجماعية: فتح / إنهاء / تغيير العنوان / الحالة
المكتبة: Telethon

التثبيت:
    pip install telethon

شروط العمل:
1) البوت يجب أن يكون مشرفاً في المجموعة (سوبر جروب) بصلاحية "إدارة المحادثات المرئية" (Manage video chats).
2) من يرسل الأمر يجب أن يكون مشرفاً في المجموعة.

الأوامر:
    /startvc [عنوان]   فتح مكالمة صوتية
    /endvc             إنهاء المكالمة الحالية
    /vctitle عنوان     تغيير عنوان المكالمة
    /vcstatus          معرفة هل توجد مكالمة نشطة
"""
from ABH import ABH as bot
import random
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    DiscardGroupCallRequest,
    EditGroupCallTitleRequest,
)


async def is_admin(event) -> bool:
    """التحقق أن مرسل الأمر مشرف."""
    perms = await bot.get_permissions(event.chat_id, event.sender_id)
    return bool(perms.is_admin or perms.is_creator)


async def get_active_call(chat_id):
    """إرجاع المكالمة النشطة في المجموعة (أو None)."""
    peer = await bot.get_input_entity(chat_id)
    full = await bot(GetFullChannelRequest(peer))
    return full.full_chat.call


def group_only(handler):
    async def wrapper(event):
        if not event.is_group:
            return await event.reply("هذا الأمر يعمل داخل المجموعات فقط.")
        if not await is_admin(event):
            return await event.reply("⛔ هذا الأمر للمشرفين فقط.")
        try:
            await handler(event)
        except Exception as e:
            await event.reply(f"❌ خطأ: {type(e).__name__}\n"
                              "تأكد أن البوت مشرف وعنده صلاحية إدارة المحادثات المرئية.")
    return wrapper


@bot.on(events.NewMessage(pattern=r"^/startvc(?:@\w+)?(?:\s+(.+))?$"))
@group_only
async def start_vc(event):
    if await get_active_call(event.chat_id):
        return await event.reply("ℹ️ توجد مكالمة نشطة بالفعل.")
    title = event.pattern_match.group(1)
    peer = await bot.get_input_entity(event.chat_id)
    await bot(CreateGroupCallRequest(
        peer=peer,
        random_id=random.randint(1, 2**31 - 1),
        title=title,
    ))
    await event.reply("✅ تم فتح المكالمة الصوتية.")


@bot.on(events.NewMessage(pattern=r"^/endvc(?:@\w+)?$"))
@group_only
async def end_vc(event):
    call = await get_active_call(event.chat_id)
    if not call:
        return await event.reply("ℹ️ لا توجد مكالمة نشطة.")
    await bot(DiscardGroupCallRequest(call=call))
    await event.reply("🛑 تم إنهاء المكالمة.")


@bot.on(events.NewMessage(pattern=r"^/vctitle(?:@\w+)?\s+(.+)$"))
@group_only
async def vc_title(event):
    call = await get_active_call(event.chat_id)
    if not call:
        return await event.reply("ℹ️ لا توجد مكالمة نشطة.")
    await bot(EditGroupCallTitleRequest(call=call, title=event.pattern_match.group(1)))
    await event.reply("✏️ تم تغيير عنوان المكالمة.")


@bot.on(events.NewMessage(pattern=r"^/vcstatus(?:@\w+)?$"))
@group_only
async def vc_status(event):
    call = await get_active_call(event.chat_id)
    await event.reply("🟢 توجد مكالمة نشطة." if call else "⚪ لا توجد مكالمة نشطة.")


print("البوت يعمل ✅")
bot.run_until_disconnected()
