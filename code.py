"""
إنشاء رسالة تفاعلية - Flow كامل
=================================
المراحل:
  1) نص الرسالة (إجباري)
  2) الميديا (اختياري) - صورة/فيديو واحد أو ألبوم كامل
     بعد كل ميديا يُسأل: "تريد تضيف أكثر؟"
  3) الأزرار (اختياري) - صيغة حرة عبر parse_buttons()
     - سطر جديد = صف جديد
     - "|" يفصل بين زرين بنفس الصف
     - "نص الزر - رابط"                 -> زر رابط عادي
     - "نص الزر - @username نص الرسالة"  -> زر يفتح محادثة مع نص جاهز (tg://resolve)

آخر خطوة: يرسل الرسالة النهائية تلقائياً (مو معاينة بس، هذي هي الرسالة الفعلية).

ملاحظة: الكود مبني على افتراض إن ABH تشبه Telethon:
  events.NewMessage / e.reply / e.text / e.sender_id / e.media / e.message.grouped_id
  و Button.url(text, url)
إذا الأسماء مختلفة عندك بـ ABH، بدّلها بالأماكن المعلّمة "# TODO".
"""

from ABH import *
import asyncio
import urllib.parse

# ============================================================
#  حالة كل مستخدم - مفصولة كلياً عن باقي المستخدمين
# ============================================================

class CreateMessageSession:
    def __init__(self):
        self.text = ''
        self.media = []      # كل عنصر: رسالة ميديا مفردة أو list (ألبوم)
        self.buttons = []
        self.step = 'text'   # text -> media -> buttons -> done


sessions = {}         # sender_id -> CreateMessageSession
album_buffers = {}    # sender_id -> {'grouped_id':.., 'messages':[..], 'task':asyncio.Task}

ALBUM_DEBOUNCE = 1.2  # ثانية ننتظرها بعد آخر صورة ألبوم قبل ما نعتبره خلص


# ============================================================
#  دالة الأزرار
# ============================================================

def parse_buttons(raw_text: str):
    """
    نص الزر - رابط                    -> زر رابط عادي
    نص الزر - @username نص الرسالة      -> زر يفتح محادثة مع نص جاهز
    زر1 - target1 | زر2 - target2      -> بنفس الصف
    سطر جديد                          -> صف جديد
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
                continue

            label, target = part.split(' - ', 1)
            label = label.strip()
            target = target.strip()

            if target.startswith('@'):
                pieces = target.split(' ', 1)
                username = pieces[0].lstrip('@')
                prefill_text = pieces[1] if len(pieces) > 1 else ''
                encoded_text = urllib.parse.quote(prefill_text)
                url = f'tg://resolve?domain={username}&text={encoded_text}'
            else:
                url = target

            # TODO: تأكد من اسم الكلاس الصحيح في ABH
            row.append(Button.url(label, url))

        if row:
            rows.append(row)

    return rows


# ============================================================
#  إرسال الرسالة النهائية الفعلية (مو معاينة)
# ============================================================

async def send_final_message(e, sess: CreateMessageSession):
    """
    يرسل الرسالة النهائية كما ستظهر فعلياً:
    - لو فيه ميديا: يرسلها مع النص كـ caption والأزرار تحتها
    - لو ماكو ميديا: يرسل نص عادي مع الأزرار
    - لو فيه أكثر من عنصر ميديا: يرسلهم كلهم، والنص+الأزرار على آخر رسالة
    """
    buttons = sess.buttons if sess.buttons else None

    if not sess.media:
        await e.reply(sess.text, buttons=buttons)
        return

    for i, item in enumerate(sess.media):
        is_last = (i == len(sess.media) - 1)
        caption = sess.text if is_last else None
        btns = buttons if is_last else None

        if isinstance(item, list):
            # ألبوم
            # TODO: عدّل حسب دالة إرسال الألبومات في ABH (send_file بقائمة ملفات)
            await e.client.send_file(
                e.chat_id,
                [m.media for m in item],
                caption=caption,
                buttons=btns,
            )
        else:
            # عنصر مفرد
            # TODO: عدّل حسب دالة إرسال الميديا في ABH
            await e.client.send_file(
                e.chat_id,
                item.media,
                caption=caption,
                buttons=btns,
            )


# ============================================================
#  بدء العملية
# ============================================================

@ABH.on(events.NewMessage(pattern=r'^انشاء رسال[هة]$'))
async def create_message_handler(e):
    sessions[e.sender_id] = CreateMessageSession()
    await e.reply('ارسل نص الرسالة:')


# ============================================================
#  إنهاء الألبوم بعد فترة سكوت
# ============================================================

async def finalize_album(e, sess: CreateMessageSession, sender_id):
    await asyncio.sleep(ALBUM_DEBOUNCE)
    buf = album_buffers.pop(sender_id, None)
    if not buf:
        return

    sess.media.append(buf['messages'])
    await ask_add_more(e)


async def ask_add_more(e):
    await e.reply('تمام. تريد تضيف ميديا اكثر؟ (نعم / لا)')


# ============================================================
#  الراوتر الرئيسي - Handler واحد ثابت
# ============================================================

@ABH.on(events.NewMessage)
async def router(e):
    sender_id = e.sender_id
    sess = sessions.get(sender_id)
    if not sess:
        return

    if e.text in ('انشاء رسالة', 'انشاء رساله'):
        return

    # ------------------------------------------------------
    # 1) النص
    # ------------------------------------------------------
    if sess.step == 'text':
        if not e.text:
            await e.reply('لازم ترسل نص:')
            return

        sess.text = e.text
        sess.step = 'media'
        await e.reply('ارسل الميديا او اكتب تخطي:')
        return

    # ------------------------------------------------------
    # 2) الميديا
    # ------------------------------------------------------
    if sess.step == 'media':
        txt = (e.text or '').strip()

        if txt in ('تخطي', 'تخطى', 'لا'):
            sess.step = 'buttons'
            await e.reply(
                'ارسل الازرار، او اكتب تخطي\n\n'
                'مثال:\n'
                'زر1 - رابط\n'
                'زر2 - @username نص الرسالة\n'
                'زر3 - target | زر4 - target'
            )
            return

        if txt == 'نعم':
            await e.reply('ارسل الميديا:')
            return

        if not e.media:
            await e.reply('ارسل صورة/فيديو، او اكتب تخطي:')
            return

        # TODO: تأكد من اسم grouped_id الصحيح في ABH
        grouped_id = getattr(e.message, 'grouped_id', None)

        if grouped_id:
            buf = album_buffers.get(sender_id)
            if buf and buf['grouped_id'] == grouped_id:
                buf['messages'].append(e.message)
                buf['task'].cancel()
            else:
                buf = {'grouped_id': grouped_id, 'messages': [e.message], 'task': None}
                album_buffers[sender_id] = buf

            buf['task'] = asyncio.create_task(finalize_album(e, sess, sender_id))
        else:
            sess.media.append(e.message)
            await ask_add_more(e)
        return

    # ------------------------------------------------------
    # 3) الأزرار + الإرسال النهائي
    # ------------------------------------------------------
    if sess.step == 'buttons':
        sess.buttons = parse_buttons(e.text or '')
        sess.step = 'done'

        await send_final_message(e, sess)

        # هنا تقدر تحفظ sess بقاعدة بيانات قبل ما تمسح الجلسة
        del sessions[sender_id]
        return
