from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
import subprocess, asyncio, sys, os, random, asyncio
from telethon.errors import ChannelPrivateError
from telethon.tl.types import Channel  
from telethon import events, Button
from telethon.tl.types import User
from datetime import datetime
from Resources import *
from ABH import *
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)
@ABH.on(events.NewMessage(pattern=r"^رفع(?:\s+(.+))?$", from_users=[wfffp]))
async def upload(e):
    custom_name = e.pattern_match.group(1)
    target_msg = None
    if e.media:
        target_msg = e
    elif e.is_reply:
        replied = await e.get_reply_message()
        if replied and replied.media:
            target_msg = replied
    if not target_msg:
        return
    msg = await e.reply("⏳ جاري الرفع...")
    try:
        if custom_name:
            temp_path = await target_msg.download_media(file="/tmp/")
            ext = os.path.splitext(temp_path)[1]
            file_name = custom_name.strip()
            if not os.path.splitext(file_name)[1]:
                file_name += ext
            final_path = os.path.join(MEDIA_DIR, file_name)
            if os.path.exists(final_path):
                os.remove(final_path)
            os.rename(temp_path, final_path)
        else:
            final_path = await target_msg.download_media(file=f"{MEDIA_DIR}/")
        await msg.edit(f"✅ تم الرفع بنجاح:\n`{os.path.basename(final_path)}`")
    except Exception as ex:
        await msg.edit(f"❌ حدث خطأ أثناء الرفع:\n`{ex}`")
@ABH.on(events.NewMessage(pattern=r"^المسارات$", from_users=[wfffp]))
async def list_media(e):
    if not os.path.isdir(MEDIA_DIR):
        await e.reply("📂 المجلد فارغ أو غير موجود.")
        return
    files = sorted(os.listdir(MEDIA_DIR))
    image_exts = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", 'mp4')
    images = [f for f in files if f.lower().endswith(image_exts)]
    if not images:
        await e.reply("📂 لا توجد صور في مجلد media.")
        return
    text = "🖼 **أسماء الصور الموجودة:**\n\n" + "\n".join(f"• `{name}`" for name in images)
    await e.reply(text)
@ABH.on(events.NewMessage(pattern=r"^مسار\s+(.+)$", from_users=[wfffp]))
async def send_by_path(e):
    file_name = e.pattern_match.group(1).strip()
    exact_path = os.path.join(MEDIA_DIR, file_name)
    target_path = None
    if os.path.isfile(exact_path):
        target_path = exact_path
    else:

        if os.path.isdir(MEDIA_DIR):
            for f in os.listdir(MEDIA_DIR):
                if os.path.splitext(f)[0] == file_name:
                    target_path = os.path.join(MEDIA_DIR, f)
                    break
    if not target_path:
        await e.reply(f"⚠️ لم يتم العثور على ملف باسم:\n`{file_name}`")
        return
    msg = await e.reply("⏳ جاري الإرسال...")
    try:
        await e.client.send_file(e.chat_id, target_path, reply_to=e.id)
        await msg.delete()
    except Exception as ex:
        await msg.edit(f"❌ حدث خطأ أثناء الإرسال:\n`{ex}`")
@ABH.on(events.NewMessage(pattern=r'^حظر من استخدام البوت (.+)$', from_users=[wfffp]))
async def global_ban(e):
    ف = await to(e)
    target_id = getattr(ف, "sender_id", None) or getattr(ف, "id", None)
    r.sadd("gbanusers", target_id)
    m = await ment(target_id)
    await e.reply(f"👤 المستخدم {m} \n✅ تم حظره عام من استخدام البوت.")
@ABH.on(events.NewMessage(pattern=r'^الغاء حظر من استخدام البوت (.+)$', from_users=[wfffp]))
async def global_unban(e):
    input_text = e.pattern_match.group(1).strip()
    ف = await to(e) 
    target_id = getattr(ف, "sender_id", None) or getattr(ف, "id", None)
    r.srem("gbanusers", target_id)        
    m = await ment(target_id) 
    await e.reply(f"✅ تم الغاء الحظر العام عن: {m}")
@ABH.on(events.NewMessage(pattern=r'^قائمة المحظورين عام$', from_users=[wfffp]))
async def list_gbanned(e):
    banned_list = r.smembers("gbanusers")
    if not banned_list:
        return await e.reply("📍 قائمة الحظر العام فارغة.")
    msg = "📝 **قائمة المحظورين عام:**\n\n"
    for index, uid in enumerate(banned_list, 1):
        uid_str = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
        msg += f"{index} - `{uid_str}`\n"    
    await e.reply(msg)
@ABH.on(events.NewMessage)
async def gban_handler(e):
    if not e.sender_id:return
    if r.sismember("gbanusers", e.sender_id):
        raise events.StopPropagation
@ABH.on(events.NewMessage(pattern='^تعيين قناة hint$', from_users=[wfffp]))
async def set_channel(event):
    message = await event.get_reply_message()
    if not message or not message.text:
        return await event.reply("⚠️ يرجى الرد على رسالة تحتوي على آيدي القناة فقط.")
    raw_id = message.text.strip()
    try:
        if raw_id.startswith("-100") or raw_id.isdigit():
            target_id = int(raw_id)
        else:
            target_id = raw_id 
        channel = await ABH.get_entity(target_id)
        if not isinstance(channel, (types.Channel, types.Chat)):
            return await event.reply("❌ هذا الآيدي لا يخص قناة أو مجموعة.")
        name = channel.title
        photo = channel.photo 
        r.set('channel_hint', str(target_id))
        caption_text = f"✅ **تم تعيين قناة الإشعارات بنجاح:**\n\n- الاسم: **{name}**\n- الآيدي: `{target_id}`"
        if photo:
            try:
                await ABH.send_file(
                    event.chat_id, 
                    photo, 
                    caption=caption_text, 
                    reply_to=event.id
                )
            except Exception:
                await event.reply(caption_text)
        else:
            await event.reply(caption_text)
    except ValueError:
        await event.reply("❌ الآيدي غير صالح، تأكد من كتابته بشكل صحيح (أرقام فقط).")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الوصول للقناة:\n`{str(e)}` \nتأكد أن البوت عضو في القناة.")
@ABH.on(events.NewMessage(pattern=r'^اعاد[هة] ال?تشغيل$', from_users=[1910015590]))
async def restart_bot(event):
    await event.reply("🔄 جاري إعادة تشغيل البوت، انتظر لحظة...")
    os.execl(sys.executable, sys.executable, *sys.argv)
@ABH.on(events.NewMessage(pattern='(event|e|الحدث)', from_users=[1910015590]))
async def sendevent(event):
    r = await event.get_reply_message()
    await hint(str(r if r else event))
    await chs(event, 'تم الارسال بالخاص')
@ABH.on(events.NewMessage(pattern="^(البنك|سرعة الاستجابة|سرعة البنك|ping)$", from_users=[wfffp]))
async def ping_test(event):
    if not event.is_group:
        return
    start_time = datetime.now()
    msg = await event.reply("🏓 قياس سرعة الاستجابة...")
    end_time = datetime.now()
    latency = (end_time - start_time).total_seconds()
    seconds = int(latency)
    milliseconds = int((latency - seconds) * 1000)
    await msg.edit(f"🏓 سرعة استجابة البوت ( {seconds:02d}:{milliseconds:03d} ) ثانية")
@ABH.on(events.NewMessage(pattern=r'^ارسل الملفات$', from_users=[1910015590]))
async def send_all_files(event):
    try:
        folder_path = "."
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            await event.reply("❗️لا توجد ملفات متاحة للإرسال في المجلد.")
            return
        await event.reply(f"📤 جارٍ إرسال {len(files)} ملفًا، يرجى الانتظار...")
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            await ABH.send_file(1910015590, file=file_path)
        await event.reply("✅ تم إرسال جميع الملفات بنجاح.")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء إرسال الملفات: {e}")
@ABH.on(events.NewMessage(pattern=r'^ارسل ملف (.+)$', from_users=[1910015590]))
async def send_file(event):
    file_name = event.pattern_match.group(1)
    if not os.path.exists(file_name):
        return await event.reply("❗️الملف غير موجود.")
    await event.reply("📤 جاري ارسال الملف...")
    await ABH.send_file(event.chat_id, file=file_name)
@ABH.on(events.NewMessage(pattern=r'^حذف ملف (.+)$', from_users=[1910015590]))
async def delete_file(event):
    file_name = event.pattern_match.group(1)
    if not os.path.exists(file_name):
        return await event.reply("الملف غير موجود.")
    os.remove(file_name)
    await event.reply("✅ تم حذف الملف بنجاح.")
@ABH.on(events.NewMessage(pattern=r'^الملفات$', from_users=[1910015590]))
async def list_files(event):
    files = os.listdir('.')
    if not files:
        return await event.reply("❗️لا توجد ملفات في المجلد الحالي.")
    file_list = "\n".join(files)
    await event.reply(f"📂 قائمة الملفات\n{file_list}")
@ABH.on(events.NewMessage(pattern=r'^اسطر الملفات$', from_users=[1910015590]))
async def list_file_lines(event):
    files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.endswith('.py')]
    if not files:
        return await event.reply("❗️لا توجد ملفات قابلة للقراءة (عدا .py).")
    output = "📄 أسماء الملفات وعدد الأسطر:\n\n"
    for file in files:
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)
            output += f"- {file} ~ {line_count}\n"
        except:
            output += f"- {file} ~ خطأ بالقراءة\n"
    await event.reply(output)
@ABH.on(events.NewMessage(pattern='^(عدد الاسطر|العدد|العدد الكلي)$', from_users=[1910015590]))
async def allline(e):
    files = os.listdir('.')
    total_lines = 0
    text = e.text
    if text == 'العدد الكلي':
        for filename in files:
            if os.path.isfile(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        total_lines += sum(1 for _ in f)
                except Exception:
                    pass
    else:
        for filename in files:
            if filename.endswith('.py') and os.path.isfile(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        total_lines += sum(1 for _ in f)
                except Exception:
                    pass
    await e.reply(f"📄 إجمالي عدد الأسطر البوت: {total_lines}")
xxx = [1910015590, 6520830528]
@ABH.on(events.NewMessage(pattern=r"^ارسل (.+)$", from_users=xxx))
async def send_handler(event):
    x = event.sender_id
    r = await event.get_reply_message()
    if not r:return
    target = event.pattern_match.group(1)
    entity = None
    try:
        if target.startswith("@"):
            entity = await ABH.get_entity(target)
        elif target.isdigit():
            entity = await ABH.get_entity(int(target))
        else:
            entity = await ABH.get_entity(target)
        await ABH.send_message(entity, r)
    except UserIsBlockedError:
        await event.reply("🚫 المستخدم حاظر البوت.")
        return
    except PeerIdInvalidError:
        await event.reply(" المستخدم ما مفعل البوت .")
        return
    except Exception as e:
        await hint(f" خطأ غير متوقع: {e}")
        return
    await chs(event, "تم الارسال بنجاح." if x == wfffp else 'عذرا ماعندك صلاحية تستخدم هذا الامر')
@ABH.on(events.NewMessage(pattern='^مخفي غادر$'))
async def logout(e):
    uid = e.sender_id
    if uid == 1910015590:
       await send(e, "تم المغادرة من مجموعتكم والسبب جان طلب المطور الاساسي")
       await e.reply('تدلل يالزعيم')
       await ABH(LeaveChannelRequest(e.chat_id))
    else:
        await e.respond(file='https://t.me/recoursec/21', reply_to=e.id)
@ABH.on(events.NewMessage(pattern=r'^اضف ملف$', from_users=[1910015590]))
async def add_file(event):
    if not event.is_reply:
        await event.reply("🔷 يجب الرد على رسالة تحتوي على ملف.")
        return
    reply = await event.get_reply_message()
    if not reply.file:
        await event.reply("🔷 الرسالة المُشار إليها لا تحتوي على ملف.")
        return
    filename = reply.file.name or "unnamed_file"
    cwd = os.getcwd()
    target_path = os.path.join(cwd, filename)
    temp_path = await reply.download_media(file=f"temp_{filename}")
    if os.path.exists(target_path):
        with open(target_path, "ab") as original_file, open(temp_path, "rb") as new_file:
            original_file.write(b"\n")
            original_file.write(new_file.read())
        os.remove(temp_path)
        await event.reply(f"✅ تم **إضافة محتوى جديد** إلى الملف: `{filename}`")
    else:
        os.rename(temp_path, target_path)
        await event.reply(f"📁 تم **إنشاء ورفع ملف جديد** باسم: `{filename}`")
@ABH.on(events.NewMessage(pattern=r'^رفع الملف$', from_users=[1910015590]))
async def upload_file(event):
    if not event.is_reply:
        await event.reply("🔷 يجب أن ترد على رسالة تحتوي ملف.")
        return
    reply = await event.get_reply_message()
    if not reply.file:
        await event.reply("🔷 هذه الرسالة لا تحتوي على ملف.")
        return
    filename = reply.file.name or "downloaded_file"
    cwd = os.getcwd()
    target_path = os.path.join(cwd, filename)
    if os.path.exists(target_path):
        os.remove(target_path)
        await event.reply(f"🗑️ تم حذف الملف القديم: `{filename}`")
    await reply.download_media(file=target_path)
    await event.reply(f"✅ تم رفع الملف وحفظه باسم: `{filename}`")
@ABH.on(events.NewMessage(pattern='مخفي اطلع'))
async def memkikme(event):
    if not event.is_group:
        return
    o = await get_owner(event)
    await react(event, '😡')
    id = event.sender_id
    if id == o.id:
        await event.reply('هاي عود انت المالك')
        return
    elif id == 1910015590:
        ء = random.choice(['مطور جيس حب انت', ' ها ابن هاشم سالمين'])
        await event.reply(ء)        
        return
    elif is_assistant(event.chat_id, event.sender_id):
        await event.reply('ديله عيني تره انزلك من المعاونين!!!')
        return
    elif not is_assistant(event.chat_id, event.sender_id):
        ء = random.choice(['توكل', 'مصدك نفسك يالعضو؟', 'هوه انت عضو تريد تطردني؟', 'طرد'])
        await event.reply(ء)
        return
@ABH.on(events.NewMessage(pattern=r"/screenlog|لوك", from_users=[1910015590]))
async def get_screen_log(event):
    session_name = "n"
    temp_full_log = "/tmp/full_log.txt"
    temp_tail_log = "/tmp/screen_tail.txt"    
    try:
        subprocess.run(
            ["screen", "-S", session_name, "-X", "hardcopy", "-h", temp_full_log],
            check=True
        )        
        subprocess.run(
            f"tail -n 500 {temp_full_log} > {temp_tail_log}", 
            shell=True, 
            check=True
        )        
        await ABH.send_file(
            1910015590,
            temp_tail_log,
            caption="📄 آخر 500 سطر من سجل شاشة البوت"
        )
        await event.reply('✅ تم استخراج آخر 500 سطر وإرسالها للخاص.')
    except subprocess.CalledProcessError:
        await hint(f'❌ فشل استخراج السجل. تأكد أن الجلسة `{session_name}` تعمل.')
    except Exception as e:
        await hint(f'⚠️ حدث خطأ: {str(e)}')
    finally:
        for file in [temp_full_log, temp_tail_log]:
            if os.path.exists(file):
                os.remove(file)
        await event.respond("⚠️ حدث خطأ أثناء قراءة سجل screen.\nتحقق من اسم الجلسة أو صلاحيات الوصول.")
CHANNEL_KEY = 'anymousupdate'
ch = r.get(CHANNEL_KEY)
buttons = Button.url('🫆', url=f'https://t.me/{ch}')
async def chs(event, c):
    await ABH.send_message(event.chat_id, c, reply_to=event.id, buttons=buttons)
async def run_cmd(command: str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode
# @ABH.on(events.NewMessage(pattern="^(تحديث|up)$", from_users=[1910015590]))
# async def update_repo(event):
#     try:
#         stdout, stderr, code = await run_cmd("git pull")
#         if code == 0:
#             await event.reply(f" تم تحديث السورس بنجاح\n\n{stdout or 'لا توجد تحديثات'}")
#             os.execv(sys.executable, [sys.executable, os.path.abspath("config.py")])
#         else:
#             await hint(f" حدث خطأ أثناء التحديث:\n\n{stderr}")
#     except Exception as e:
#         await hint(f"⚠️ خطأ غير متوقع:\n\n{e}")
@ABH.on(events.NewMessage(pattern=r'^تعيين قناة chs (.+)', from_users=[1910015590]))
async def add_channel(event):
    global CHANNEL_KEY
    ch = event.pattern_match.group(1)
    x = r.exists(CHANNEL_KEY)
    await event.reply(f" تم اضافة قيمة القناة{ch}")
    if x:
        r.delete(CHANNEL_KEY)
    r.set(CHANNEL_KEY, ch)
    await event.reply(f" تم حفظ القناة {ch}")
    CHANNEL_KEY = ch
@ABH.on(events.NewMessage(pattern=r'^عرض قناة chs$', from_users=[1910015590]))
async def show_channel(event):
    ch = r.get(CHANNEL_KEY)
    if ch:
        await event.reply(f"📡 القناة المحفوظة: @{ch}")
    else:
        await event.reply("⚠️ لا توجد قناة محفوظة.")
@ABH.on(events.NewMessage(pattern=r'^تعيين قناة الكروب (.+)$'))
async def add_group_channel(event):
    if not event.is_group: 
        return
    a = await auth(event)
    if not a or a not in ('المالك', 'المطور الاساسي'):     
        return await event.reply("⚠️ الامر يخص المالك فقط!!!.")    
    target_channel = event.pattern_match.group(1)    
    try:
        entity = await event.client.get_entity(target_channel)
        if isinstance(entity, Channel) and entity.broadcast:
            channel_name = entity.title
            channel_id = entity.id
            success_text = (
                f"✅ **تم تعيين قناة المجموعة بنجاح!**\n\n"
                f"─── اسم القناة: **{channel_name}**\n"
                f"─── ايدي القناة: `{channel_id}`"
            )
            r.set(f'group:{e.chat_id}', entity.id)
            return await event.reply(success_text)
        else:
            return await event.reply("❌ **خطأ:** الرابط أو المعرف المرسل لا يعود لـ (قناة) عامة!")
    except ChannelPrivateError:
        return await event.reply("⚠️ **خطأ:** القناة خاصة ولا يمكن للحساب فحصها أو الوصول إليها.")        
    except Exception as e:
        await hint(f'⚠️ حدث خطأ أثناء التحقق:**`' + str(e) + '`')    
        return await event.reply(f"⚙️ **حدث خطأ أثناء الفحص:**`")    
REDIS_KEY = "users"
session = {}
msg_data = {}
callbacknames = {
    'posting_commands': 'اوامر النشر', 
    'banned_commands': "اوامر المحظورين", 
    'subscribe_commands': 'اوامر الاشتراك الاجباري'
}
async def send_admin_menu(event_or_message, is_callback=False):
    admin_buttons = [
        [Button.inline("اوامر النشر", data='posting_commands'),
         Button.inline("اوامر المحظورين", data='banned_commands')],
        [Button.inline("اوامر الاشتراك الاجباري", data='subscribe_commands')]
    ]
    text = '**أهلاً زعيم، شنو تحب تسوي؟ 👇🏾**'
    if is_callback:
        await event_or_message.edit(text, buttons=admin_buttons)
    else:
        await event_or_message.reply(text, buttons=admin_buttons)
years, months, days  = get_years_months_days('2025-1-25')
@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    id = e.sender_id
    if id == wfffp:
        return await send_admin_menu(e, is_callback=False)
    id = e.sender_id
    if profile(id):
        b = Button.inline("👤 تعديل حسابك", data=f"Edit_{id}")
    else:
        b = Button.inline("🔑 تسجيل الدخول", data=f"login_{id}")
    user_buttons = [
        [Button.url("➕ أضفني لمجموعتك", url="https://t.me/vipabh_bot?startgroup=true&admin=banusers+delete_messages+restrict_members+invite_users+pin_messages+change_info")],
        [Button.url("📢 القناة", url=f"https://t.me/{CHANNEL_KEY}"),b]]
    mention_user = await mention(e)
    caption_text = (
        f"مرحباً عزيزي ( {mention_user} )، أنا اسمي **مخفي** وعمري ( {years} سنة و {months} أشهر ) ✨\n\n"
        f"🛡️ أنا بوت حماية متقدم، تواجدي داخل مجموعتك يضمن لها حماية كاملة من الباند والتعطيل، "
        f"بالإضافة إلى باقة من الألعاب المميزة والفريدة من نوعها بروح وفكرة جديدة! 🕹️"
    )
    await e.reply(caption_text, buttons=user_buttons)
@ABH.on(events.CallbackQuery(pattern=r'(posting_commands|banned_commands|subscribe_commands|back_to_main)'))
async def admin_menu_callbacks(event):
    data = event.data.decode()    
    if data == 'back_to_main':
        return await send_admin_menu(event, is_callback=True)
    if data == 'posting_commands':
        buttons = [
            [Button.inline("انشاء رسالة", data='creat_message'),
             Button.inline("التقاط رسالة", data='catch_message')],
            [Button.inline("🔙 عودة", data='back_to_main')] 
        ]
    elif data == 'banned_commands':
        buttons = [
            [Button.inline("حظر عضو", data='banuser'),
             Button.inline("الغاء حظر عضو", data='unbanuser')],
            [Button.inline("المحظورين", data='banned_users')],
            [Button.inline("🔙 عودة", data='back_to_main')]
        ]
    elif data == 'subscribe_commands':
        userslen = r.scard('users')
        buttons = [
            [Button.inline(f"المستخدمين ( {userslen} )", data='all_users'),
             Button.inline("جلب اسامي المستخدمين", data='users_names')],
            [Button.inline("البحث عن مستخدم", data='serch_user')],
            [Button.inline("🔙 عودة", data='back_to_main')] 
        ]        
    await event.edit(f'اختر احد الازرار من قائمة {callbacknames.get(data, "")}', buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=r'(creat_message|catch_message|banned_users|users_names|more:)'))
async def features_callbacks(e):
    data = e.data.decode()
    id = e.sender_id
    raw_users = list(r.smembers('users'))
    all_users = [str(uid.decode() if isinstance(uid, bytes) else uid).strip() for uid in raw_users]
    all_users = [uid for uid in all_users if not uid.startswith('-')]
    if data == "creat_message":
        create_msg_buttons = [
            [Button.inline("تعيين نص", data='set_captin')],
            [Button.inline("تعيين ميديا", data='set_media')],
            [Button.inline("تعيين زر", data='set_button')]
        ]
        await e.edit('اختر محتوى الرسالة المُراد إنشاؤها:', buttons=create_msg_buttons)
    elif data == 'catch_message':
        await e.edit("📥 أرسل الآن الرسالة (نص، صورة، متحركة...) ليتم توجيهها ونشرها للمشتركين:")
        session[id] = data
    elif data == 'banned_users':
        banned_users = r.smembers("gbanusers")
        if not banned_users:
            return await e.edit("لا يوجد محظورين حالياً.")
        m = await mentions(banned_users)
        await e.edit('\n'.join(m))
    elif data == 'users_names':
        m = await mentions(all_users[:20])
        b = [Button.inline("اظهار المزيد ➡️", data='more:1')]
        await e.edit('\n'.join(m), buttons=[b], parse_mode='md', link_preview=False)
    elif data.startswith('more:'):
        page = int(data.split(':')[1])        
        start_idx = page * 20
        end_idx = start_idx + 20        
        current_slice = all_users[start_idx:end_idx]
        if not current_slice:
            return await e.answer("📋 تم عرض جميع أعضاء البوت بنجاح!", alert=True)            
        result = await mentions(current_slice)
        buttons_row = []
        if page > 1:
            buttons_row.append(Button.inline("⬅️ السابق", data=f'more:{page-1}'))
        if len(all_users) > end_idx:
            buttons_row.append(Button.inline("إظهار المزيد ➡️", data=f'more:{page+1}'))
        buttons = [buttons_row] if buttons_row else []
        buttons.append([Button.inline("❌ إغلاق القائمة", data="back_to_main")])
        await e.edit('\n'.join(result), buttons=buttons, parse_mode='md', link_preview=False)
@ABH.on(events.CallbackQuery(pattern=r'(banuser|unbanuser|serch_user|set_captin|set_media|set_button)'))
async def inputs_request_callbacks(e):
    data = e.data.decode()
    sender_id = e.sender_id    
    if data.startswith('set_'):
        session[sender_id] = data
        action = {'set_captin': 'النص الأساسي', 'set_media': 'الميديا (صورة/فيديو)', 'set_button': 'نص الزر الشفاف'}
        return await e.edit(f'📥 **أرسل الآن {action[data]} للرسالة:**')
    await e.edit('🔍 **أرسل الآن يوزر أو آيدي الشخص المطلوب:**')
    session[sender_id] = data    
    await asyncio.sleep(120)
    if sender_id in session and session[sender_id] == data:
        session.pop(sender_id, None)
        await e.respond('⚠️ **انتهت مهلة الطلب (120 ثانية)، يرجى المحاولة مجدداً.**')
@ABH.on(events.NewMessage)
async def get_user_inputs_handler(event):
    sender_id = event.sender_id
    if sender_id not in session: return
    data = session[sender_id]
    if data.startswith('set_') or data in ['set_button_url']:
        if sender_id not in msg_data:
            msg_data[sender_id] = {}
        if data == 'set_captin':
            msg_data[sender_id]['text'] = event.text
            session[sender_id] = 'set_media'
            return await event.reply('✅ تم حفظ النص.\n📥 الآن أرسل الميديا المطلوبة (أو أرسل /skip لتخطي الميديا):')
        elif data == 'set_media':
            if event.text == '/skip':
                msg_data[sender_id]['media'] = None
            elif event.media:
                msg_data[sender_id]['media'] = event.media
            else:
                return await event.reply("❌ يرجى إرسال ميديا صالحة أو أرسل /skip للتخطي:")
            session[sender_id] = 'set_button' 
            return await event.reply('✅ تم حفظ الميديا.\n⌨️ الآن أرسل النص الذي تريده أن يظهر على الزر الشفاف:')
        elif data == 'set_button':
            msg_data[sender_id]['button_text'] = event.text
            session[sender_id] = 'set_button_url'
            return await event.reply('✅ تم حفظ نص الزر.\n🔗 الآن أرسل رابط الزر الشفاف (يجب أن يبدأ بـ http:// أو https://):')
        elif data == 'set_button_url':
            if not event.text.startswith(('http://', 'https://')):
                return await event.reply("❌ الرابط غير صالح! أرسل رابطاً حقيقياً يبدأ بـ http:")
            msg_data[sender_id]['button_url'] = event.text
            await event.reply('🎉 **ممتاز! تم اكتمال تجهيز رسالتك المخصصة بنجاح.**\nيمكنك الآن إرسالها للنشر عبر أزرار التحكم الفرعية.')
            session.pop(sender_id, None)
            return
    if data == 'catch_message':
        b = [
            [Button.inline('نعم، ابدأ النشر', data=f'yes:{event.chat_id}:{event.id}'),
             Button.inline('لا، إلغاء', data=f'no:{event.chat_id}:{event.id}')]
        ]
        session.pop(sender_id, None) 
        return await event.reply('❓ هل أنت متأكد من رغبتك في نشر وتوجيه هذه الرسالة لجميع المشتركين؟', buttons=b)
    text = event.text
    target = await to(event, text=text)
    if not target: 
        return await event.reply('❌ **يرجى إرسال يوزر أو آيدي صالح!**')
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    if data == 'banuser':
        r.sadd("gbanusers", str(target_id)) 
        m = await ment(target_id)
        await event.reply(f'🚫 تم حظر {m} بنجاح من البوت.')
        session.pop(sender_id, None)
    elif data == 'unbanuser':
        r.srem("gbanusers", str(target_id))
        m = await ment(target_id)
        await event.reply(f'✅ تم فك حظر {m} بنجاح.')
        session.pop(sender_id, None)
    elif data == 'serch_user':
        photo = await get_profile_photo(target_id)
        caption = f'''
👤 **بيانات المستخدم الشخصية:**
• الاسم الأول: {target.first_name}
• الحساب: {await ment(target_id)}
• الآيدي: `{target_id}`
• الترتيب: `{get_order(target_id) or "لا يوجد"}`
        '''
        session.pop(sender_id, None)
        if photo:
            await ABH.send_file(event.chat_id, photo, caption=caption, reply_to=event.id)
        else:
            await ABH.send_message(event.chat_id, message=caption, reply_to=event.id)
@ABH.on(events.CallbackQuery(pattern=r'(yes|no)'))
async def broadcast_confirmation_callbacks(e):
    data = e.data.decode()
    if ':' not in data: return
    data = data.split(':')
    if len(data) != 3: return
    arg, from_chat, msg_id = data
    if arg == 'yes':
        count = r.scard('users')
        await e.edit(f'🚀 جارٍ بدء عملية النشر التلقائي لـ {count} محادثة...')
        raw_users = list(r.smembers('users'))
        users = [uid.decode() if isinstance(uid, bytes) else str(uid) for uid in raw_users]
        done = 0
        for user_id in users:
            send = await try_forward(e, chat=from_chat, id=msg_id, to=user_id)
            if send: 
                done += 1
        caption = f'📊 **تقرير اكتمال النشر الإذاعي:**\n\n✅ تم بنجاح إرسال: `{done}` من أصل `{count}`\n❌ فشل إرسال: `{count - done}` محادثة.'
        await e.reply(caption)
    elif arg == 'no':
        await e.edit('❌ تم إلغاء جلسة النشر وتطهير العمليات بنجاح.')
