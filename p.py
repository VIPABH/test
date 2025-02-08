from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon import TelegramClient, events
import os
import time

async def extract_time(cat, time_val):
    if any(time_val.endswith(unit) for unit in ("s", "m", "h", "d", "w")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await cat.edit("الوقت الذي تم تحديده غير صحيح")
            return None
        if unit == "s":
            bantime = int(time.time() + int(time_num) * 1)
        elif unit == "m":
            bantime = int(time.time() + int(time_num) * 60)
        elif unit == "h":
            bantime = int(time.time() + int(time_num) * 60 * 60)
        elif unit == "d":
            bantime = int(time.time() + int(time_num) * 24 * 60 * 60)
        elif unit == "w":
            bantime = int(time.time() + int(time_num) * 7 * 24 * 60 * 60)
        else:
            await cat.edit(
                f"خطأ في تحديد الوقت. اكتب من الأسفل:\n s, m, h, d, أو w: {time_val[-1]}"
            )
            return None
        return bantime
    await cat.edit(
        f"خطأ في تحديد الوقت. اكتب من الأسفل:\n s, m, h, d, أو w: {time_val[-1]}"
    )
    return None

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

joker_t8ed = "https://forkgraph.zaid.pro/file/ya744KD7Km3q"
joker_unt8ed = "https://forkgraph.zaid.pro/file/YMTcYN1GaXQy"

@ABH.on(
    events.NewMessage(pattern="تقييد_مؤقت(?:\s|$)([\s\S]*)")
)
async def tmuter(event):
    # التحقق من أن الأمر تم إرساله في مجموعة
    if not event.is_group:
        return await event.edit("⚠️ هذا الأمر يعمل فقط في المجموعات.")

    # التحقق من أن المستخدم لديه صلاحية تقييد الأعضاء
    sender = await event.get_sender()
    if not sender.admin_rights or not sender.admin_rights.ban_users:
        return await event.edit("❌ ليس لديك صلاحية لتقييد الأعضاء.")

    # الحصول على المستخدم الذي تم الرد عليه
    replied_message = await event.get_reply_message()
    if not replied_message:
        return await event.edit("⚠️ يرجى الرد على رسالة المستخدم الذي تريد تقييده.")

    user = replied_message.sender_id
    if not user:
        return await event.edit("❌ لم أتمكن من العثور على المستخدم.")

    # استخراج الوقت والسبب
    reason = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else None
    if not reason:
        return await event.edit("᯽︙ انـت لم تقـم بـوضـع وقـت مع الامـر")

    reason_parts = reason.split(" ", 1)
    cattime = reason_parts[0].strip()
    reason = reason_parts[1].strip() if len(reason_parts) > 1 else None

    # استخراج الوقت
    ctime = await extract_time(event, cattime)
    if not ctime:
        return

    # التحقق من أن المستخدم لا يحاول تقييد نفسه
    if user == event.client.uid:
        return await event.edit("᯽︙ عـذرا لا يمـكننـي حـظر نفـسي")

    try:
        # تنفيذ التقييد
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user,
                ChatBannedRights(until_date=ctime, send_messages=True),
            )
        )

        # إرسال رسالة التأكيد
        if reason:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"᯽︙ تم تقييد المستخدم {replied_message.sender.first_name} [@{replied_message.sender.username or 'N/A'}] بنجاح ✅\n ᯽︙ السبب: {reason}\n ** ᯽︙ مدة التقييد: **`{cattime}`",
            )
        else:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"**᯽︙ تم تقييد المستخدم {replied_message.sender.first_name} [@{replied_message.sender.username or 'N/A'}] بنجاح ✓** \n** ᯽︙ مدة التقييد: **`{cattime}`",
            )

    except UserIdInvalidError:
        return await event.edit("**يبدو ان كتم الشخص تم الغائه**")
    except UserAdminInvalidError:
        return await event.edit(
            "** يبـدو أنك لسـت مشرف في المجموعة او تحاول كتم مشـرف هنا**"
        )
    except Exception as e:
        return await event.edit(f"`{str(e)}`")

# بدء تشغيل البوت
print("✅ البوت يعمل... انتظر الأوامر!")
ABH.run_until_disconnected()
