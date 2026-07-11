from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio


class Game:
    """يمثل جلسة لعبة واحدة داخل مجموعة معيّنة."""

    def __init__(self, owner_id):
        self.owner = owner_id
        self.players = {}          # user_id -> {"name": str, "points": int}
        self.current_killer = None
        self.started = False       # يمنع تشغيل اللعبة مرتين بالتوازي
        self.killer_event = asyncio.Event()  # بديل عن الـ polling بـ sleep(1)

        self.doctor = None         # يُختار مرة وحدة لكامل اللعبة، وما يتعوض إذا مات
        self.protected = None      # اللاعب المحمي بالجولة الحالية
        self.doctor_event = asyncio.Event()

    # ---- إدارة اللاعبين ----
    def add_player(self, user_id, name):
        self.players[user_id] = {"name": name, "points": 2}

    def remove_player(self, user_id):
        return self.players.pop(user_id, None)

    def is_player(self, user_id):
        return user_id in self.players

    # ---- إدارة القاتل ----
    def set_killer(self, user_id):
        self.current_killer = user_id
        self.killer_event.clear()

    def get_killer(self):
        return self.current_killer

    def del_killer(self):
        self.current_killer = None
        self.killer_event.set()   # يفك أي انتظار عالق فورًا

    # ---- إدارة الطبيب ----
    def assign_doctor(self):
        """يختار طبيب عشوائي مرة وحدة عند بدء اللعبة."""
        self.doctor = random.choice(list(self.players.keys()))
        return self.doctor

    def doctor_alive(self):
        return self.doctor is not None and self.doctor in self.players

    def set_protected(self, user_id):
        self.protected = user_id
        self.doctor_event.set()

    def clear_protected(self):
        self.protected = None
        self.doctor_event.clear()

    def end(self):
        self.players.clear()
        self.current_killer = None
        self.doctor = None
        self.protected = None
        self.killer_event.set()
        self.doctor_event.set()


games = {}  # chat_id -> Game


def end_game(chat_id):
    """تنهي اللعبة وتحذفها من القاموس العام حتى يمكن بدء لعبة جديدة."""
    game = games.pop(chat_id, None)
    if game:
        game.end()


# ---------------------------------------------------------------------------
# بدء اللعبة والانضمام
# ---------------------------------------------------------------------------

@ABH.on(events.NewMessage(pattern='^(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    user = e.sender_id
    if chat in games:
        return await e.reply("اللعبة قيد التشغيل بالفعل")

    m = await mention(e)
    my = await ABH.get_me()
    b = Button.url('اضغط هنا للانضمام', url=f"https://t.me/{my.username}?start=killamorder_{chat}")
    await e.reply(f"تم تشغيل لعبة القاتل والمقتول \n انت مالك اللعبة ( {m} )", buttons=[b])

    game = Game(user)
    game.add_player(user, m)
    games[chat] = game


@ABH.on(events.NewMessage(pattern=r'^/start killamorder_(-?[0-9]+)$'))
async def join_game(e):
    chat_id = int(e.pattern_match.group(1))
    game = games.get(chat_id)
    if not game:
        return await e.reply("لا توجد لعبة شغالة في هذه المجموعة")
    if game.started:
        return await e.reply("اللعبة بدأت بالفعل، انتظر الجولة الجاية")
    if game.is_player(e.sender_id):
        return await e.reply("أنت بالفعل داخل اللعبة!")

    m = await mention(e)
    game.add_player(e.sender_id, m)
    await e.reply(f"تم إضافتك للعبة بنجاح! عدد اللاعبين الآن: {len(game.players)}")


@ABH.on(events.NewMessage(pattern='^اللاعبين$'))
async def show_players(e):
    game = games.get(e.chat_id)
    if not game:
        return
    lines = [f'{p["name"]}  -  {p["points"]}' for p in game.players.values()]
    await e.reply("اللاعبين:\n" + "\n".join(lines))


@ABH.on(events.NewMessage(pattern='^انسحب$'))
async def leave_game(e):
    """يسمح للاعب بالانسحاب من اللعبة قبل بدايتها."""
    game = games.get(e.chat_id)
    if not game or game.started:
        return
    if not game.is_player(e.sender_id):
        return await e.reply("أنت لست داخل اللعبة")
    game.remove_player(e.sender_id)
    await e.reply("تم انسحابك من اللعبة")


@ABH.on(events.NewMessage(pattern='^(/endgame|إنهاء اللعبة)$'))
async def force_end_game(e):
    """يسمح للمالك بإنهاء اللعبة يدويًا في أي وقت."""
    game = games.get(e.chat_id)
    if not game:
        return await e.reply("لا توجد لعبة شغالة")
    if e.sender_id != game.owner:
        return await e.reply("بس مالك اللعبة يكدر ينهيها")
    end_game(e.chat_id)
    await e.reply("تم إنهاء اللعبة")


# ---------------------------------------------------------------------------
# منطق اللعب
# ---------------------------------------------------------------------------

@ABH.on(events.NewMessage(pattern='^تم$', incoming=True))
async def start_game(e):
    chat = e.chat_id
    game = games.get(chat)
    if not game:
        return
    if e.sender_id != game.owner:
        return await e.reply("أنت لست مالك اللعبة")
    if game.started:
        return  # اللعبة شغالة أصلًا، تجاهل الضغطة المكررة
    if len(game.players) < 2:
        return await e.reply("لازم لاعبين اثنين على الأقل عشان تبدأ اللعبة")

    game.started = True
    doctor_id = game.assign_doctor()
    try:
        await ABH.send_message(
            doctor_id,
            "أنت الطبيب السري بهذي اللعبة 🩺\n"
            "كل جولة راح أسألك مين تريد تحمي قبل ما يتحرك القاتل.\n"
            "إذا مت، ما راح يكون في طبيب بديل لبقية اللعبة."
        )
    except Exception:
        pass  # ممكن الطبيب مسوي بلوك للبوت بالخاص، اللعبة تكمل بدون إشعاره

    await e.reply("يتم بدء اللعبة ...")

    while chat in games and len(games[chat].players) > 1:
        game = games[chat]

        if game.doctor_alive():
            await ask_doctor_protect(e, game)
            game.doctor_event.clear()
            try:
                await asyncio.wait_for(game.doctor_event.wait(), timeout=20)
            except asyncio.TimeoutError:
                game.protected = None  # الطبيب ما تصرف، ماكو حماية هالجولة

        await set_auto_killer(e, game)
        if chat not in games:
            break
        game = games[chat]

        # ننتظر إما إن القاتل يتصرف، أو تنتهي مهلة 30 ثانية
        game.killer_event.clear()
        try:
            await asyncio.wait_for(game.killer_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            # القاتل ما تصرف بالوقت المحدد -> نلغي دوره بدون قتل أحد
            if game.get_killer() is not None:
                skipped = game.players.get(game.get_killer())
                if skipped:
                    await e.reply(f"انتهى وقت ( {skipped['name']} ) ولم يقتل أحد")
                game.del_killer()

        await asyncio.sleep(random.randint(3, 6))


async def ask_doctor_protect(e, game):
    """يرسل للطبيب بالخاص أزرار لاختيار مين يحمي هالجولة."""
    btns = [[Button.inline(p["name"], data=f"protect:{uid}")]
            for uid, p in game.players.items()]
    btns.append([Button.inline("بدون حماية هالجولة", data="protect_skip")])
    try:
        await ABH.send_message(game.doctor, "مين تريد تحمي هالجولة؟ (عندك 20 ثانية)", buttons=btns)
    except Exception:
        game.protected = None  # ما كدرنا نوصله، اللعبة تكمل بدون حماية


async def set_auto_killer(e, game):
    chat = e.chat_id
    players = game.players

    if not players:
        end_game(chat)
        return

    if len(players) == 1:
        winner_id, winner = next(iter(players.items()))
        await e.reply(f"🎉 مبارك للاعب ( {winner['name']} ) - محاولاته المتبقية: {winner['points']}")
        end_game(chat)
        return

    player_id, pdata = random.choice(list(players.items()))

    if pdata["points"] <= 0:
        await e.reply(f"الله يرحمك ( {pdata['name']} ) — ماتت نقاطك")
        game.remove_player(player_id)
        return

    game.set_killer(player_id)
    game.players[player_id]["points"] -= 1

    btns = [
        Button.inline("تحديد الضحية", data="choice_to_kill"),
        Button.inline("قتل عشوائي", data="autokill"),
    ]
    await e.reply(f"أنت القاتل يا ( {pdata['name']} ) — اختر نوع القتل (30 ثانية)", buttons=btns)


@ABH.on(events.CallbackQuery(pattern=r"protect:(\d+)|protect_skip"))
async def doctor_callback(e):
    """يعالج اختيار الطبيب من رسالته الخاصة."""
    game = next((g for g in games.values() if g.doctor == e.sender_id), None)
    if not game or not game.doctor_alive():
        return await e.answer("لا توجد لعبة نشطة لك كطبيب حاليًا", alert=True)

    data = e.data.decode()
    if data == "protect_skip":
        game.set_protected(None)
        return await e.edit("تمام، ما راح تحمي أحد هالجولة")

    target_id = int(data.split(":")[1])
    if target_id not in game.players:
        return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)

    game.set_protected(target_id)
    target_name = game.players[target_id]["name"]
    await e.edit(f"تمام، راح تحمي ( {target_name} ) هالجولة")


@ABH.on(events.CallbackQuery(pattern=r"choice_to_kill|autokill|kill:(\d+)"))
async def kill_callback(e):
    chat = e.chat_id
    game = games.get(chat)
    if not game:
        return await e.answer("لا توجد لعبة نشطة", alert=True)

    killer = game.get_killer()
    if not killer or e.sender_id != killer:
        return await e.answer("أنت لست القاتل!", alert=True)

    data = e.data.decode()
    players = game.players

    if data == "autokill":
        candidates = {uid: p for uid, p in players.items() if uid != killer}
        if not candidates:
            game.del_killer()
            return await e.edit("لا يوجد لاعبين آخرين لقتلهم")
        victim_id, victim = random.choice(list(candidates.items()))
        game.del_killer()
        if victim_id == game.protected:
            game.protected = None
            await e.edit(f"القاتل حاول يقتل ( {victim['name']} ) لكن الطبيب أنقذه! 🩺")
        else:
            game.remove_player(victim_id)
            await e.edit(f"تم قتل اللاعب ( {victim['name']} )")
        return

    if data == "choice_to_kill":
        btns = [[Button.inline(p["name"], data=f"kill:{uid}")]
                for uid, p in players.items() if uid != killer]
        if not btns:
            return await e.answer("لا يوجد لاعبين آخرين", alert=True)
        return await e.edit("اختر الضحية:", buttons=btns)

    if data.startswith("kill:"):
        victim_id = int(data.split(":")[1])
        if victim_id not in players:
            return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)
        victim_name = players[victim_id]["name"]
        game.del_killer()
        if victim_id == game.protected:
            game.protected = None
            await e.edit(f"القاتل حاول يقتل ( {victim_name} ) لكن الطبيب أنقذه! 🩺")
        else:
            game.remove_player(victim_id)
            await e.edit(f"تم قتل ( {victim_name} ) بنجاح")
