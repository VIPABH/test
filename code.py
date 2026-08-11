import logging
import re
from urllib.parse import urlparse

from ABH import *
from telethon import Button
from telethon.tl.types import MessageEntityCustomEmoji

log = logging.getLogger("zar_buttons")

COLORS = {
    "ازرق": "primary",
    "أزرق": "primary",
    "إزرق": "primary",
    "blue": "primary",

    "احمر": "danger",
    "أحمر": "danger",
    "إحمر": "danger",
    "red": "danger",

    "اخضر": "success",
    "أخضر": "success",
    "إخضر": "success",
    "green": "success",
}

MAX_BUTTONS = 20
MAX_LABEL_LEN = 64
MAX_INVALID_SHOWN = 5


def normalize_word(word: str) -> str:
    """توحيد صيغ الهمزات حتى تتطابق كلمات الألوان بمختلف كتاباتها."""
    word = word.lower().strip()
    word = word.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return word


def valid_url(url: str) -> bool:
    try:
        if url.startswith("tg://"):
            return True
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def utf16_len(s: str) -> int:
    """طول النص بوحدات UTF-16 (هذا ما تعتمده Telegram في إزاحات الـ entities)."""
    return len(s.encode("utf-16-le")) // 2


def split_with_positions(text: str, sep: str):
    """يقسم النص على sep مع إرجاع موضع كل جزء (بعدد المحارف) داخل النص الأصلي."""
    parts = []
    start = 0
    for chunk in text.split(sep):
        idx = text.index(chunk, start)
        parts.append((chunk, idx))
        start = idx + len(chunk)
    return parts


def find_custom_emoji_id(entities, raw_text: str, token: str, token_offset_codepoints: int):
    """
    يبحث في entities الرسالة عن MessageEntityCustomEmoji تطابق موضع/طول
    الأيقونة المكتوبة، ويرجع document_id إذا وجد، وإلا None.
    """
    if not entities:
        return None

    utf16_offset = utf16_len(raw_text[:token_offset_codepoints])
    utf16_length = utf16_len(token)

    for ent in entities:
        if not isinstance(ent, MessageEntityCustomEmoji):
            continue
        # تطابق تام أو تداخل مقبول في حال فروقات بسيطة بالمسافات
        if ent.offset == utf16_offset and ent.length == utf16_length:
            return ent.document_id
        if (ent.offset <= utf16_offset < ent.offset + ent.length):
            return ent.document_id

    return None


@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):

    # if not event.is_group:
    #     return

    match = event.pattern_match
    full_text = match.group(1)

    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بعد الأمر، بصيغة:\n\n"
            "`زر [اللون] [اسم الزر] الرابط [الايموجي]`\n\n"
            "مثال:\n"
            "`زر ازرق المطور https://t.me/k_4x1 🌚`\n\n"
            "اللون والايموجي اختياريان.\n"
            "لإضافة زر جديد استخدم `|`"
        )

    if not event.is_reply:
        return await event.reply(
            "يجب الرد على الرسالة التي تريد نسخها."
        )

    reply_msg = await event.get_reply_message()

    if reply_msg is None:
        return await event.reply(
            "تعذّر العثور على الرسالة المردود عليها، ربما تم حذفها."
        )

    raw_text = event.raw_text or ""
    entities = event.message.entities or []
    full_text_start = match.start(1)  # موضع بداية full_text داخل raw_text (بعدد المحارف)

    items_with_pos = [
        (item, pos) for item, pos in split_with_positions(full_text, "|")
        if item.strip()
    ]

    if len(items_with_pos) > MAX_BUTTONS:
        return await event.reply(
            f"الحد الأقصى هو {MAX_BUTTONS} زرًا."
        )

    buttons = []
    row = []
    invalid = []

    for raw_item, item_pos in items_with_pos:

        item = raw_item.strip()
        lstrip_diff = len(raw_item) - len(raw_item.lstrip())
        item_offset = item_pos + lstrip_diff  # موضع item بعد الإزالة، داخل full_text

        # نجمع أجزاء العنصر مع مواضعها (بعدد المحارف) داخل full_text
        token_matches = list(re.finditer(r"\S+", item))

        if not token_matches:
            invalid.append(raw_item)
            continue

        parts = [m.group(0) for m in token_matches]

        # البحث عن الرابط
        url_index = None
        for i, value in enumerate(parts):
            if value.startswith(("http://", "https://", "tg://")):
                url_index = i
                break

        if url_index is None:
            invalid.append(raw_item)
            continue

        url = parts[url_index]

        if not valid_url(url):
            invalid.append(raw_item)
            continue

        # ------------------------------------------------
        # كل شيء قبل الرابط = اللون + الاسم
        # ------------------------------------------------

        before_url = parts[:url_index]

        style = None
        label_parts = before_url

        if before_url:
            first_normalized = normalize_word(before_url[0])
            if first_normalized in COLORS:
                style = COLORS[first_normalized]
                label_parts = before_url[1:]

        label = " ".join(label_parts).strip()

        if not label:
            label = "اضغط هنا"

        if len(label) > MAX_LABEL_LEN:
            invalid.append(raw_item)
            continue

        # ------------------------------------------------
        # ما بعد الرابط = الأيقونة (نص أو ايموجي مميز/كستم)
        # ------------------------------------------------

        after_url = parts[url_index + 1:]

        if len(after_url) > 1:
            invalid.append(raw_item)
            continue

        icon = None

        if after_url:
            icon_token = after_url[0]
            icon_match = token_matches[url_index + 1]

            # موضع الأيقونة الكامل داخل raw_text (بعدد المحارف)
            token_offset_codepoints = full_text_start + item_offset + icon_match.start()

            custom_emoji_id = find_custom_emoji_id(
                entities, raw_text, icon_token, token_offset_codepoints
            )

            if custom_emoji_id is not None:
                # أيقونة إيموجي مميز (custom emoji) — نستخدم الـ document_id مباشرة
                icon = custom_emoji_id
            else:
                # إيموجي/نص عادي: لا يوجد تحديد طول تعسفي، فقط حد معقول للتسلسلات
                # (بعض الإيموجيات المركّبة تستهلك عدة كود بوينت عبر ZWJ)
                if len(icon_token) > 16:
                    invalid.append(raw_item)
                    continue
                icon = icon_token

        # ------------------------------------------------
        # إنشاء الزر
        # ------------------------------------------------

        try:
            button = Button.url(
                label,
                url,
                style=style,
                icon=icon,
            )
        except TypeError:
            # المكتبة المستخدمة لا تدعم style/icon كمعاملات
            log.warning("Button.url لا يدعم style/icon، إنشاء الزر بدونها: %s", raw_item)
            try:
                button = Button.url(label, url)
            except Exception as e:
                log.exception("فشل إنشاء زر حتى بعد إزالة style/icon: %s", raw_item)
                invalid.append(raw_item)
                continue
        except Exception as e:
            log.exception("فشل إنشاء الزر للعنصر: %s", raw_item)
            invalid.append(raw_item)
            continue

        row.append(button)

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    if not buttons:
        return await event.reply(
            "لم يتم العثور على أي أزرار صالحة."
        )

    warning = ""
    if invalid:
        invalid_text = "\n".join(
            # استبدال أي backtick داخل النص حتى لا يكسر تنسيق Markdown
            f"• `{x.replace('`', chr(39))}`"
            for x in invalid[:MAX_INVALID_SHOWN]
        )
        warning = f"\n\n⚠️ تم تجاهل بعض الأزرار:\n{invalid_text}"
        if len(invalid) > MAX_INVALID_SHOWN:
            warning += f"\n... و {len(invalid) - MAX_INVALID_SHOWN} أخرى."

    try:
        if reply_msg.media:
            await ABH.send_file(
                event.chat_id,
                reply_msg.media,
                caption=reply_msg.message or "",
                buttons=buttons,
            )
        elif reply_msg.message:
            await ABH.send_message(
                event.chat_id,
                reply_msg.message,
                buttons=buttons,
            )
        else:
            return await event.reply(
                "لا يمكن نسخ نوع هذه الرسالة."
            )

        try:
            await event.delete()
        except Exception:
            log.debug("تعذّر حذف رسالة الأمر (صلاحيات غالبًا).")

        if warning:
            await ABH.send_message(
                event.chat_id,
                f"تم إنشاء الأزرار بنجاح.{warning}"
            )

    except Exception:
        log.exception("فشل إرسال الرسالة النهائية مع الأزرار.")
        return await event.reply(
            "حدث خطأ أثناء إنشاء الرسالة والأزرار."
        )
