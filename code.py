from ABH import *
import os, asyncio, uuid, gc, matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from Resources import *
import seaborn as sns
import pandas as pd
matplotlib.use("Agg")


async def download_group_background(chat, bg_path: str):
    try:
        photo = getattr(chat, "photo", None)
        if not photo:
            await hint("🔍 تشخيص: الكروب ماعنده chat.photo (مافيه صورة بروفايل أصلاً)")
            return None

        await hint(f"🔍 تشخيص: نوع chat.photo = {type(photo).__name__}, chat_id = {getattr(chat, 'id', '?')}")

        path = await ABH.download_profile_photo(chat.id, file=bg_path, download_big=False)

        if not path or not os.path.exists(bg_path):
            await hint(f"🔍 تشخيص: فشل تحميل صورة الكروب بـ chat.id. path={path}, exists={os.path.exists(bg_path)}")
            return None
        # تصغير الصورة إذا كانت كبيرة، حتى نقلل استهلاك الذاكرة وقت الرسم
        # (السيرفر بموارد محدودة 1GB رام، فنخلي الصورة صغيرة قد الإمكان)
        from PIL import Image
        with Image.open(bg_path) as pil_img:
            pil_img.thumbnail((400, 400))
            return mpimg.pil_to_array(pil_img.convert("RGB"))
    except Exception as err:
        await hint(f"❌ خطأ في تحميل صورة الكروب: {type(err).__name__}: {err}")
        return None


async def resolve_users(user_ids):
    users_dict = {}
    for uid in user_ids:
        name_val = profile(uid)
        if name_val and isinstance(name_val, dict):
            users_dict[uid] = name_val.get("name")
            continue
        try:
            user = await ABH.get_entity(uid)
            users_dict[uid] = user.first_name if hasattr(user, "first_name") else "مستخدم"
        except Exception:
            users_dict[uid] = "مستخدم"
    return users_dict


def _draw_chart(plot_data: pd.DataFrame, background, output_path: str):
    """
    الجزء الثقيل (matplotlib) — دالة sync عادية تشتغل بخيط منفصل
    عن طريق run_in_executor حتى ما تبلك الـ event loop وقت الرسم.
    """
    plt.close("all")  # تنظيف أي رسومات قديمة متراكمة بالذاكرة من محاولات سابقة
    messages = plot_data["messages"].tolist()
    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        _render(fig, ax, plot_data, messages, background)
        fig.savefig(output_path, dpi=100, bbox_inches="tight")
    finally:
        plt.close(fig)  # نضمن قفل الرسمة بأي حالة (نجاح أو خطأ) حتى ما تصير تسريبات ذاكرة
        gc.collect()  # تنظيف ذاكرة صريح — مهم بسيرفر موارده محدودة
    return output_path


def _render(fig, ax, plot_data, messages, background):
    sns.barplot(
        data=plot_data,
        x="messages",
        y="name",
        hue="name",
        palette="viridis",
        legend=False,
        ax=ax,
    )
    ax.invert_yaxis()
    if background is not None:
        # تطبيق الخلفية: تغطي كامل مساحة الرسمة (0 إلى 1 بإحداثيات المحور)
        # بغض النظر عن قيم البيانات، وترسم ورا الأعمدة (zorder واطي).
        ax.imshow(background, extent=[0, 1, 0, 1], transform=ax.transAxes, aspect="auto", zorder=0)
        ax.axis("off")
        title_color = "white"
        text_color = "white"
    else:
        title_color = "black"
        text_color = "black"
    ax.set_title("أكثر 10 أعضاء إرسالاً للرسائل", fontsize=18, color=title_color, pad=20)
    ax.set_xlabel("")
    ax.set_ylabel("")
    max_val = max(messages) if messages else 0
    for i, value in enumerate(messages):
        ax.text(
            value + max_val * 0.01,
            i,
            str(value),
            va="center",
            color=text_color,
        )
    try:
        plt.tight_layout()
    except Exception:
        pass  # تجاهل التحذير لو تعذر ضبط الهوامش (لا يؤثر على النتيجة النهائية)


async def generate_top10_chart(e):
    """
    داله شاملة وذكية تسوي كل شي بنفسها:
    1) تسترجع بيانات الأسبوع من stats.json
    2) تجيب أسماء المستخدمين وتبني الشارت (برسم بخيط منفصل عشان ما تبلك البوت)
    3) ترسل الصورة كرد على رسالة المستخدم
    4) تحذف الملفات المؤقتة (خلفية + صورة الشارت) بأي حالة (نجاح أو فشل)

    ترجع True إذا نجحت العملية، وترسل رسالة خطأ عن طريق hint() إذا صار خطأ.
    """
    if not e.is_group:
        return False

    row_data = create('stats.json')
    data = row_data.get('weekly', {}).get(str(e.chat_id), {})
    if not data:
        await chs(e, 'ماكو معلومات كافية حته امثل بيها البيانات')
        return False

    msg = await e.reply('⏳ جاري جلب البيانات وتصميم الصورة، انتظر لحظة...')

    uid_token = uuid.uuid4().hex[:8]
    bg_path = f"group_bg_{e.chat_id}_{uid_token}.jpg"
    output_path = f"weekly_top10_{e.chat_id}_{uid_token}.png"

    try:
        user_ids = [int(uid) for uid in data.keys()]
        users_dict = await resolve_users(user_ids)
        names = [users_dict.get(uid, "مستخدم") for uid in user_ids]
        counts = [int(data[str(uid)]) for uid in user_ids]

        plot_data = pd.DataFrame({'name': names, 'messages': counts})
        plot_data = plot_data.sort_values('messages', ascending=False).head(10)

        chat = await e.get_chat()
        background = await download_group_background(chat, bg_path)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _draw_chart, plot_data, background, output_path)

        await ABH.send_file(
            e.chat_id,
            output_path,
            caption="🏆 أكثر 10 أعضاء إرسالاً للرسائل أسبوعياً",
            reply_to=e.id,
        )
        await msg.delete()
        return True
    except Exception as ex:
        await hint(f'صار خطأ اثناء تمثيل البيانات: {ex}')
        return False
    finally:
        if os.path.exists(bg_path):
            os.remove(bg_path)
        if os.path.exists(output_path):
            os.remove(output_path)


@ABH.on(events.NewMessage(pattern=r'^تمثيل البيانات$', from_users=[wfffp]))
async def count_pic(e):
    if not authers(await auth(e), 'المطور الثانوي'):
        return await chs(e, 'عذرا الامر يخص المطور الثانوي وفوك')
    if not lock(e, 'توب'):
        return await chs(e, 'عذرا بس التوب معطل')
    await generate_top10_chart(e)
