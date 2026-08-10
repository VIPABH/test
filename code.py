"""
إنشاء رسالة تفاعلية - Flow كامل
=================================
المراحل:
  1) نص الرسالة (إجباري)
  2) الميديا (اختياري) - يدعم صورة/فيديو واحد أو ألبوم (عدة صور برسالة وحدة)
     بعد كل ميديا يُسأل المستخدم: "هل تريد إضافة المزيد؟"
  3) الأزرار (اختياري) - صيغة حرة يتحكم بيها parse_buttons()
     - سطر جديد  = صف جديد من الأزرار
     - "|"       = يفصل بين زرين بنفس الصف
     - نوع الزر الأول:  "نص الزر - رابط"                -> زر رابط عادي
     - نوع الزر الثاني: "نص الزر - @username نص الرسالة" -> زر يفتح محادثة
       المستخدم مع رسالة معبأة مسبقاً عبر tg://resolve

بعد كل خطوة تُرسل معاينة (Preview) للرسالة بحالتها الحالية.

ملاحظة مهمة:
هذا الكود مبني على افتراض أن مكتبة ABH تشبه Telethon من ناحية:
  - events.NewMessage / e.reply / e.text / e.sender_id / e.media
  - e.message.grouped_id  لتمييز رسائل الألبوم (قد يختلف الاسم عندك، عدّله حسب توثيق ABH)
  - كلاس Button (Button.url(text, url)) لإرسال الأزرار
إذا كانت التسميات مختلفة في ABH، بدّلها بنفس الأماكن المعلّق عليها بـ "# TODO".
"""

from ABH import *
import asyncio
import urllib.parse

# ============================================================
#  حالة كل مستخدم (Session) - مفصولة بالكامل عن باقي المستخدمين
# ============================================================

class CreateMessageSession:
    def __init__(self):
        self.text = ''
        self.media = []      # كل عنصر: إما رسالة ميديا مفردة أو list (ألبوم)
        self.buttons_raw = ''
        self.buttons = []    # نتيجة parse_buttons النهائية
        self.step = 'text'   # text -> media -> buttons -> done


sessions = {}          # sender_id -> CreateMessageSession
album_buffers = {}      # sender_id -> {'grouped_id':.., 'messages':[..], 'task':asyncio.Task}

ALBUM_DEBOUNCE = 1.2    # ثانية ننتظرها بعد آخر رسالة ألبوم قبل ما نعتبره اكتمل


# ============================================================
#  دالة الأزرار - بالتنسيق اللي حددته
# ============================================================

def parse_buttons(raw_text: str):
    """
    تحوّل نص الأزرار الخام إلى صفوف أزرار (list of list of Button).

    الصيغة:
        نص الزر - https://example.com               -> زر رابط عادي
        نص الزر - @username نص الرسالة المطلوب إرسالها  -> زر يفتح محادثة اليوزر
                                                          مع نص جاهز عبر tg://resolve
        زر1 - target1 | زر2 - target2                -> بنفس الصف
        (سطر جديد)                                    -> صف جديد

    إذا كان النص فاضي أو = "تخطي" ترجع [].
    """
    raw_text = (raw_text or '').strip()
    if not raw_text or raw_text in ('تخطي', 'تخطى'):
        return []

    rows = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        row = []
        for part in line.split('|'):
            part = part.strip()
            if ' - ' not in part:
                # صيغة غير صحيحة، نتجاهل هذا الزر بدل ما نفشل الرسالة كلها
                continue

            label, target = part.split(' - ', 1)
            label = label.strip()
            target = target.strip()

            if target.startswith('@'):
                # نوع 2: زر يفتح محادثة مع المستخدم ونص جاهز
                # الصيغة: @username نص الرسالة
                pieces = target.split(' ', 1)
                username = pieces[0].lstrip('@')
                prefill_text = pieces[1] if len(pieces) > 1 else ''
                encoded_text = urllib.parse.quote(prefill_text)
                url = f'tg://resolve?domain={username}&text={encoded_text}'
            else:
                # نوع 1: زر رابط عادي
                url = target

            # TODO: تأكد من اسم الكلاس الصحيح في ABH (Button.url أو غيره)
            row.append(Button.url(label, url))

        if row:
            rows.append(row)

    return rows


# ============================================================
#  المعاينة (Preview) - تُرسل بعد كل خطوة
# ============================================================

async def send_preview(e, sess: CreateMessageSession, note: str = ''):
    """
    ترسل معاينة للرسالة بحالتها الحالية (نص + آخر ميديا مضافة + الأزرار إن وجدت).
    """
    header = '📋 معاينة الرسالة الحالية:\n\n'
    body = sess.text or '(بدون نص بعد)'
    footer = ''
    if sess.media:
        footer += f'\n\n🖼 عدد عناصر/ألبومات الميديا المضافة: {len(sess.media)}'
    if note:
        footer += f'\n\n{note}'

    buttons = sess.buttons if sess.buttons else None

    # إرسال نص + أزرار كمعاينة نصية دايماً (بسيط وآمن)
    await e.reply(header + body + footer, buttons=buttons)

    # لو فيه ميديا، أعد إرسال آخر عنصر/ألبوم مضاف كمعاينة بصرية
    if sess.media:
        last = sess.media[-1]
        if isinstance(last, list):
            # ألبوم: أعد إرساله كمجموعة
            # TODO: عدّل حسب دالة إرسال الألبومات الفعلية في ABH
            await e.client.send_file(e.chat_id, [m.media for m in last])
        else:
            # عنصر مفرد
            # TODO: عدّل حسب دالة إرسال الميديا الفعلية في ABH
            await e.client.send_file(e.chat_id, last.media)


# ============================================================
#  بدء العملية
# ============================================================

@ABH.on(events.NewMessage(pattern=r'^انشاء رسال[هة]$'))
async def create_message_handler(e):
    sessions[e.sender_id] = CreateMessageSession()
    await e.reply('🛠 يجري إنشاء رسالة جديدة...')
    await asyncio.sleep(1)
    await e.reply('✍️ أرسل الآن نص الرسالة:')


# ============================================================
#  إنهاء الألبوم بعد فترة سكوت (Debounce)
# ============================================================

async def finalize_album(e, sess: CreateMessageSession, sender_id):
    await asyncio.sleep(ALBUM_DEBOUNCE)
    buf = album_buffers.pop(sender_id, None)
    if not buf:
        return

    sess.media.append(buf['messages'])  # نضيف الألبوم كوحدة واحدة (list)
    await ask_add_more(e, sess)


async def ask_add_more(e, sess: CreateMessageSession):
    await send_preview(e, sess, note='✅ تمت إضافة الميديا.')
    await asyncio.sleep(0.5)
    await e.reply('➕ هل تريد إضافة المزيد من الميديا؟ (اكتب: نعم / لا)')
    # يبقى step = 'media'، وبانتظار رد المستخدم بـ نعم/لا أو ميديا جديدة مباشرة


# ============================================================
#  الراوتر الرئيسي - Handler واحد ثابت لكل الرسائل
# ============================================================

@ABH.on(events.NewMessage)
async def router(e):
    sender_id = e.sender_id
    sess = sessions.get(sender_id)
    if not sess:
        return  # المستخدم مو داخل عملية إنشاء رسالة

    if e.text in ('انشاء رسالة', 'انشاء رساله'):
        return  # هذا الأمر يعالجه create_message_handler فقط

    # ------------------------------------------------------
    # المرحلة 1: النص
    # ------------------------------------------------------
    if sess.step == 'text':
        if not e.text:
            await e.reply('⚠️ لازم ترسل نص. حاول مرة ثانية:')
            return

        sess.text = e.text
        sess.step = 'media'
        await send_preview(e, sess, note='✅ تم حفظ النص.')
        await asyncio.sleep(0.5)
        await e.reply('🖼 أرسل الآن الميديا (صورة/فيديو/ألبوم)، أو اكتب "تخطي":')
        return

    # ------------------------------------------------------
    # المرحلة 2: الميديا (يدعم ألبومات)
    # ------------------------------------------------------
    if sess.step == 'media':
        # المستخدم يريد تخطي الميديا كلياً أو إنهاء الإضافة
        if e.text and e.text.strip() in ('تخطي', 'تخطى'):
            sess.step = 'buttons'
            await send_preview(e, sess, note='⏭ تم تخطي الميديا.')
            await asyncio.sleep(0.5)
            await e.reply(
                '🔘 أرسل الآن الأزرار بهذه الصيغة، أو اكتب "تخطي":\n\n'
                'نص الزر - رابط\n'
                'نص الزر - @username نص الرسالة\n'
                'زر1 - target1 | زر2 - target2   (لنفس الصف)\n'
                '(سطر جديد لكل صف جديد)'
            )
            return

        if e.text and e.text.strip() == 'لا':
            sess.step = 'buttons'
            await e.reply(
                '🔘 أرسل الآن الأزرار بهذه الصيغة، أو اكتب "تخطي":\n\n'
                'نص الزر - رابط\n'
                'نص الزر - @username نص الرسالة\n'
                'زر1 - target1 | زر2 - target2   (لنفس الصف)\n'
                '(سطر جديد لكل صف جديد)'
            )
            return

        if e.text and e.text.strip() == 'نعم':
            await e.reply('🖼 أرسل الميديا الإضافية الآن:')
            return

        if not e.media:
            await e.reply('⚠️ هذي مو ميديا. أرسل صورة/فيديو، أو اكتب "تخطي" أو "لا".')
            return

        # TODO: تأكد من اسم الخاصية الصحيحة لـ grouped_id في ABH (قد تكون e.message.grouped_id)
        grouped_id = getattr(e.message, 'grouped_id', None)

        if grouped_id:
            # جزء من ألبوم
            buf = album_buffers.get(sender_id)
            if buf and buf['grouped_id'] == grouped_id:
                buf['messages'].append(e.message)
                buf['task'].cancel()
            else:
                buf = {'grouped_id': grouped_id, 'messages': [e.message], 'task': None}
                album_buffers[sender_id] = buf

            buf['task'] = asyncio.create_task(finalize_album(e, sess, sender_id))
        else:
            # ميديا مفردة
            sess.media.append(e.message)
            await ask_add_more(e, sess)
        return

    # ------------------------------------------------------
    # المرحلة 3: الأزرار
    # ------------------------------------------------------
    if sess.step == 'buttons':
        sess.buttons_raw = e.text or ''
        sess.buttons = parse_buttons(sess.buttons_raw)
        sess.step = 'done'

        await send_preview(e, sess, note='✅ تم إنشاء الرسالة بنجاح.')
        await asyncio.sleep(0.5)
        await e.reply('🎉 اكتملت الرسالة! أرسل "انشاء رسالة" لإنشاء رسالة جديدة.')

        # هنا تقدر تحفظ sess (نص + ميديا + أزرار) بقاعدة بيانات قبل ما تمسح الجلسة
        del sessions[sender_id]
        return
