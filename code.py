import redis
from ABH import *
from telethon import TelegramClient, events
session_aliases = {}
@ABH.on(events.NewMessage(incoming=True))
async def execute_alias_engine(event):
    # if not event.is_group or not event.raw_text:
    #     return
    chat_id = event.chat_id
    text = event.raw_text
    parts = text.split(maxsplit=1)
    if not parts:
        return
    incoming_shortcut = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""    
    real_cmd = r.hget(f"cmd:{chat_id}", incoming_shortcut)    
    if real_cmd:
        event.raw_text = f"{real_cmd} {args}"        
        try:
            event._parse_msg()
            await ABH._dispatch_event(event)
        except:
            pass
@ABH.on(events.NewMessage(pattern=r'^اختصار$'))
async def start_alias_session(event):
    # if not event.is_group: return        
    a = await auth(event)
    if not a or a == 'المعاون': 
        return await chs(event, قفل('المساعد وفوق'))
    chat_id, user_id = event.chat_id, event.sender_id
    if chat_id not in session_aliases: session_aliases[chat_id] = {}
    session_aliases[chat_id][user_id] = {"step": "waiting_old", "old_command": None}
    await event.reply('**الآن أرسل الأمر القديم (الأصلي) كما هو تماماً:**')
    ABH.add_event_handler(
        get_aliases_handler, 
        events.NewMessage(chats=chat_id, from_users=user_id)
    )    
    await asyncio.sleep(60)
    if chat_id in session_aliases and user_id in session_aliases[chat_id]:
        del session_aliases[chat_id][user_id]
        ABH.remove_event_handler(get_aliases_handler)
async def get_aliases_handler(event):
    chat_id, user_id = event.chat_id, event.sender_id
    if chat_id not in session_aliases or user_id not in session_aliases[chat_id]:
        return
    session = session_aliases[chat_id][user_id]
    if session["step"] == "waiting_old":
        session["old_command"] = event.text.strip()
        session["step"] = "waiting_new"
        await event.reply(f"**حسناً، الأصل هو:** `{session['old_command']}`\n**الآن أرسل كلمة الاختصار الجديدة:**")
    elif session["step"] == "waiting_new":
        new_alias = event.text.strip().lower()
        old_command = session["old_command"]                
        r.hset(f"cmd:{chat_id}", new_alias, old_command)
        await event.reply(f"✅ تم بنجاح:\n**{new_alias}** ↫ **{old_command}**")        
        await send(event, f"تم إضافة اختصار جديد:\nالأصل: `{old_command}`\nالمختصر: `{new_alias}`")
        del session_aliases[chat_id][user_id]
        ABH.remove_event_handler(get_aliases_handler)
@ABH.on(events.NewMessage(pattern=r'^(حذف|مسح) اختصار (.+)'))
async def remove_alias(event):
    a = await auth(event)
    if not a or a == 'المعاون': return    
    chat_id = event.chat_id
    target = event.pattern_match.group(2).strip().lower()
    if r.hdel(f"cmd:{chat_id}", target):
        await event.reply(f"🗑 تم حذف الاختصار `{target}`")
    else:
        await event.reply(f"⚠️ الاختصار غير موجود.")
@ABH.on(events.NewMessage(pattern=r'^الاختصارات$'))
async def list_aliases(event):
    all_as = r.hgetall(f"cmd:{event.chat_id}")
    if not all_as: 
        return await event.reply("⚠️ لا توجد اختصارات حالياً.")
    res = "🔗 **اختصارات الكروب (نص خام):**\n\n"
    for s, o in all_as.items():
        res += f"• `{o}` ↫ `{s}`\n"
    await event.reply(res)
@ABH.on(events.NewMessage(pattern=r'^حذف الاختصارات$'))
async def clear_all_aliases(event):
    a = await auth(event)
    if not a or a in ('المعاون', 'المساعد'): return
    r.delete(f"cmd:{event.chat_id}")
    await event.reply("✅ تم تصفير جميع الاختصارات.")
@ABH.on(events.NewMessage(pattern='(تقييد عام|تقييد|تحذير)'))
async def _(e):
    await e.reply('شغال')
