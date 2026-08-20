import matplotlib.pyplot as plt
import os, asyncio, uuid, gc
from Resources import *
from Program import chs
import seaborn as sns
import pandas as pd
from ABH import *
async def resolve_users(user_ids):
    users_dict = {}
    for uid in user_ids:
        name_val = profile(uid)
        if name_val and isinstance(name_val, dict):
            users_dict[uid] = name_val.get("name")
            continue
        try:
            user = await ABH.get_entity(uid)
            users_dict[uid] = (
                user.first_name
                if hasattr(user, "first_name")
                else "مستخدم"
            )
        except Exception:
            users_dict[uid] = "مستخدم"
    return users_dict
def _draw_chart(plot_data: pd.DataFrame, output_path: str):
    plt.close("all")
    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        _render(fig, ax, plot_data)
        fig.savefig(
            output_path,
            dpi=100,
            bbox_inches="tight"
        )
    finally:
        plt.close(fig)
        gc.collect()
    return output_path
def _render(fig, ax, plot_data):
    messages = plot_data["messages"].tolist()
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
    ax.set_title(
        "أكثر 10 أعضاء إرسالاً للرسائل",
        fontsize=18,
        pad=20
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    max_val = max(messages) if messages else 0
    for i, value in enumerate(messages):
        ax.text(
            value + max_val * 0.01,
            i,
            str(value),
            va="center"
        )
    plt.tight_layout()
async def generate_top10_chart(e):
    if not e.is_group:return False
    row_data = create('stats.json')
    chat_id = str(e.chat_id)
    msg_id = row_data.get('mgs', {}).get(chat_id)
    old_msg = None
    if msg_id:
        old_msg = await ABH.get_messages(
            e.chat_id,
            ids=msg_id
        )
        if not old_msg:
            row_data.setdefault('mgs', {}).pop(chat_id, None)
        if old_msg and old_msg.media:
            return await ABH.send_file(
                e.chat_id,
                file=old_msg.media,
                caption=f"`{old_msg.text}`",
                reply_to=e.id
            )
    data = row_data.get(chat_id, {}).get('weekly', {})
    await hint(data)
    if not data:
        await chs(e, 'ماكو معلومات كافية حته امثل بيها البيانات')
        return False
    uid_token = uuid.uuid4().hex[:8]
    output_path = (f"weekly_top10_{e.chat_id}_{uid_token}.png")
    user_ids = [
        int(uid)
        for uid in data.keys()
        if not uid.startswith("2026-")
    ]
    await hint(user_ids)
    users_dict = await resolve_users(user_ids)
    names = [
        users_dict.get(uid, "مستخدم")
        for uid in user_ids
    ]
    counts = [
        int(data[str(uid)])
        for uid in user_ids
    ]
    plot_data = pd.DataFrame({
        'name': names,
        'messages': counts
    })
    plot_data = (
        plot_data
        .sort_values(
            'messages',
            ascending=False).head(10))
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _draw_chart,
        plot_data,
        output_path
    )
    if old_msg:
        msg = await ABH.edit_message(
            e.chat_id,
            old_msg.id,
            '🏆 أكثر 10 أعضاء إرسالاً للرسائل يومياً',
            file=output_path)
    else:
        msg = await ABH.send_file(
            e.chat_id,
            file=output_path,
            caption='🏆 أكثر 10 أعضاء إرسالاً للرسائل يومياً', 
            reply_to=e.id
        )
    row_data.setdefault('mgs', {})
    row_data['mgs'][chat_id] = msg.id
    with open('stats.json','w', encoding='utf-8') as f:
        json.dump(row_data, f, ensure_ascii=False, indent=4)
    if os.path.exists(output_path):
        os.remove(output_path)
    return msg
@ABH.on(events.NewMessage(pattern=r'^تمثيل البيانات$'))
async def count_pic(e):
    if not authers(await auth(e), 'المطور الثانوي'):
        return await chs(e,'عذرا الامر يخص المطور الثانوي وفوك')
    if not lock(e, 'توب'):
        return await chs(e,'عذرا بس التوب معطل')
    await generate_top10_chart(e)
DATA_FILE = "stats.json"
@ABH.on(events.NewMessage)
async def unified_handler(event):
    if not event.is_group: return
    l = lock(event, 'توب')
    if not l: return
    baghdad_tz = pytz.timezone("Asia/Baghdad")
    now = datetime.now(baghdad_tz)
    current_date = now.strftime("%Y-%m-%d")
    weekday = now.weekday()
    user_id = str(event.sender_id)
    chat_id = str(event.chat_id)
    last_daily_chat = r.get(f"last_daily:{chat_id}")
    if last_daily_chat is None or current_date != last_daily_chat:
        daily_hash = r.hgetall(f"daily:{chat_id}")
        if daily_hash:
            daily_sorted = sorted(
                daily_hash.items(), key=lambda x: int(x[1]), reverse=True)[:3]
            data = create('stats.json')
            data.setdefault(chat_id, {})["daily"] = {
                uid: int(c) for uid, c in daily_sorted}
            data.setdefault(chat_id, {})[current_date] = event.id
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            r.delete(f"daily:{chat_id}")
        r.set(f"last_daily:{chat_id}", current_date)
    last_weekly_chat = r.get(f"last_weekly:{chat_id}")
    if weekday == 4 and (
        last_weekly_chat is None or current_date != last_weekly_chat):
        weekly_hash = r.hgetall(f"weekly:{chat_id}")
        if weekly_hash:
            weekly_sorted = sorted(
                weekly_hash.items(), key=lambda x: int(x[1]), reverse=True)[:10]
            data = create('stats.json')
            data.setdefault(chat_id, {})["weekly"] = {
                uid: int(c) for uid, c in weekly_sorted}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            r.delete(f"weekly:{chat_id}")
        r.set(f"last_weekly:{chat_id}", current_date)
    r.hincrby(f"daily:{chat_id}", user_id, 1)
    r.hincrby(f"weekly:{chat_id}", user_id, 1)
@ABH.on(events.NewMessage(pattern="^عدد (المتفاعلين|تفاعل)$"))
async def show_interactions(e):
    if not e.is_group:return
    guid = str(e.chat_id)
    if t == "عدد المتفاعلين":
        key = f"daily:{guid}"
    else:
        key = f"weekly:{guid}"
    total = r.hlen(key)
    await chs(e, f"تفاعل الاعضاء: {total} عضو")
@ABH.on(events.NewMessage(pattern="^(توب اليومي|المتفاعلين|توب الاسبوعي|تفاعل)$"))
async def اليومي(event):
    if not event.is_group:return
    guid = str(event.chat_id)
    if event.text in ("توب اليومي", "المتفاعلين"):
        key = f"daily:{guid}"
    else:
        key = f"weekly:{guid}"
    stats = r.hgetall(key)
    if not stats:
        await event.reply("لا توجد إحصائيات بعد.")
        return
    sorted_users = sorted(
        stats.items(),
        key=lambda x: int(x[1]),
        reverse=True
    )[:10]
    top_users = []
    for idx, (uid, msg_count) in enumerate(sorted_users, 1):
        m = await ment(uid)
        top_users.append(f"{unicode}{idx}. {unicode}{m} - {unicode}{msg_count} {unicode}رسالة")
    await event.reply("\n".join(top_users))
    await react(event, "🌚")
@ABH.on(events.NewMessage(pattern=r'^(رسائله|رسائلة|الرسائل|رسائلي)$'))
async def his_res(event):
    if event.text in ('رسائلي', 'الرسائل'):
        unm1 = str(event.sender_id)
        guid1 = str(event.chat_id)
    else:
        rpl = await event.get_reply_message()
        if not rpl:
            await react(event, "🤔")
            return
        unm1 = str(rpl.sender_id)
        guid1 = str(event.chat_id)
    daily = r.hget(f"daily:{guid1}", unm1) or 0
    weekly = r.hget(f"weekly:{guid1}", unm1) or 0
    x = await info(event, None)
    total = x.get("الرسائل", 0)
    await react(event, "👍")
    await chs(
        event,
        f'اليومية: {daily}\nالاسبوعية: {weekly}\n {unicode}الكليّة: {total}'
    )
