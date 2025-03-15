from telethon import TelegramClient, events
import os, asyncio
import time

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

uinfo = {}

@ABH.on(events.NewMessage)
async def msgs(event):
    global uinfo
    # تحقق من الوقت في كل رسالة جديدة
    now = time.localtime()  # الحصول على الوقت المحلي
    # تحقق إذا كانت الساعة 2:57 مساءً
    if now.tm_hour == 15 and now.tm_min == 4:
        uinfo = {}  # مسح جميع البيانات المخزنة في القاموس uinfo
        print("تم مسح البيانات عند الساعة 2:57 مساءً.")

    if event.is_group:
        uid = event.sender.first_name
        unm = event.sender_id
        guid = event.chat_id
        if unm not in uinfo:
            uinfo[unm] = {}
        if guid not in uinfo[unm]:
            uinfo[unm][guid] = {"guid": guid, "unm": unm, "fname": uid, "msg": 1}
        else:
            uinfo[unm][guid]["msg"] += 1

@ABH.on(events.NewMessage(pattern='توب'))
async def show_res(event):
    await asyncio.sleep(2)
    guid = event.chat_id
    
    # ترتيب المستخدمين بناءً على عدد الرسائل
    sorted_users = sorted(uinfo.items(), key=lambda x: x[1][guid]['msg'], reverse=True)[:20]
    
    top_users = []
    for user, data in sorted_users:
        if guid in data:
            user_id = user  # استخدم المعرف الخاص بالمستخدم
            msg_count = data[guid]["msg"]
            top_users.append(f"المستخدم [{data[guid]['fname']}](tg://user?id={user_id}) رسائله -> {msg_count}")
    
    if top_users:
        await event.reply("\n".join(top_users))
    else:
        await event.reply("لا توجد بيانات لعرضها.")

@ABH.on(events.NewMessage(pattern='رسائله|رسائلة|رسائل|الرسائل'))
async def show_user_msgs_res(event):
    r = await event.get_reply_message()
    await asyncio.sleep(2)
    if not r:
        return
    uid1 = r.sender.first_name
    unm1 = r.sender_id
    guid1 = event.chat_id
    if unm1 in uinfo and guid1 in uinfo[unm1]:
        msg_count = uinfo[unm1][guid1]["msg"]
        await event.reply(f"المستخدم [{uid1}](tg://user?id={unm1}) أرسل {msg_count} رسالة في هذه المجموعة.")

async def main():
    await ABH.run_until_disconnected()

# تشغيل البوت
asyncio.run(main())
