from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio

killamordersession = {}

@ABH.on(events.NewMessage(pattern='(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    user = e.sender_id
    
    if chat in killamordersession:
        return await e.reply("اللعبة قيد التشغيل بالفعل")

    m = await mention(e)
    killamordersession[chat] = {
        "owner": user,
        "players": {user: {"name": m, "points": 2}},
    }

    msg = await e.reply("تم تشغيل لعبة القاتل والمقتول — أرسل (انا) للانضمام")
    killamordersession[chat]["edit"] = msg.id


@ABH.on(events.NewMessage(pattern=r'^انا$'))
async def register_player(e):
    chat = e.chat_id
    user = e.sender_id
    
    if chat not in killamordersession:
        return

    players = killamordersession[chat]["players"]

    if user in players:
        return await e.reply("سجلتك مسبقًا")

    m = await mention(e)
    players[user] = {"name": m, "points": 2}

    # تحديث قائمة اللاعبين
    msg = "تم تشغيل لعبة القاتل والمقتول — أرسل (انا) للانضمام\n"
    for P in players.values():
        msg += f"اللاعب: {P['name']}\n"

    await ABH.edit_message(chat, killamordersession[chat]["edit"], msg)
    await e.reply(f"تم تسجيلك: {m}")


@ABH.on(events.NewMessage(pattern='اللاعبين'))
async def show_players(e):
    chat = e.chat_id

    if chat not in killamordersession:
        return await e.reply("لا توجد لعبة شغالة")

    msg = "اللاعبين:\n"
    for p in killamordersession[chat]["players"].values():
        msg += f"- {p['name']}\n"

    await e.reply(msg)


@ABH.on(events.NewMessage(pattern='تم', incoming=True))
async def start_game(e):
    chat = e.chat_id

    if chat not in killamordersession:
        return

    await e.reply("يتم بدء اللعبة ...")
    players_count = len(killamordersession[chat]["players"]) * 2

    for _ in range(players_count):
        await set_auto_killer(e)
        await asyncio.sleep(10)


async def set_auto_killer(e):
    chat = e.chat_id
    session = killamordersession[chat]
    players = session["players"]

    # لا يوجد لاعبين
    if not players:
        del killamordersession[chat]
        return

    # فائز وحيد
    if len(players) == 1:
        winner = next(iter(players.values()))["name"]
        await e.reply(f"🎉 مبروك! الفائز هو: {winner}")
        del killamordersession[chat]
        return

    # اختيار القاتل
    player_id, pdata = random.choice(list(players.items()))
    killer_name = pdata["name"]
    points = pdata["points"]

    # ان مات (0 نقاط)
    if points <= 0:
        await e.reply(f"الله يرحمك ( {killer_name} ) — ماتت نقاطك")
        del players[player_id]
        return

    # حفظ القاتل
    session["killer"] = player_id

    # أزرار
    btns = [
        Button.inline("تحديد الضحية", data="choice_to_kill"),
        Button.inline("قتل عشوائي", data="autokill")
    ]

    await e.reply(f"أنت القاتل يا ( {killer_name} ) — اختر نوع القتل", buttons=btns)

    # إنقاص النقاط
    session["players"][player_id]["points"] -= 1


@ABH.on(events.CallbackQuery)
async def kill_callback(e):
    chat = e.chat_id
    session = killamordersession.get(chat)
    if not session:
        return

    killer = session.get("killer")
    if not killer or e.sender_id != killer:
        return

    data = e.data.decode()

    players = session["players"]

    if data == "autokill":  # قتل عشوائي
        victim_id, victim_data = random.choice(list(players.items()))

        if victim_id == killer:
            await e.edit(f"انتحر اللاعب ( {victim_data['name']} ) 🤦‍♂️")
            del players[victim_id]
            session["killer"] = None
            return

        await e.edit(f"تم قتل اللاعب ( {victim_data['name']} )")
        del players[victim_id]
        session["killer"] = None
        return
    if data == "choice_to_kill":  # تحديد ضحية
        txt = "اختر الضحية:\n"
        btns = []

        for uid, pdata in players.items():
            if uid != killer:
                btns.append([Button.inline(pdata["name"], data=f"kill:{uid}")])
        await e.edit(txt, buttons=btns)
        return
    if data.startswith("kill:"):
        victim_id = int(data.split(":")[1])
        victim = players[victim_id]["name"]
        del players[victim_id]
        await e.edit(f"تم قتل ( {victim} ) بنجاح")
        session["killer"] = None
