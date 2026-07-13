from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio


# ---------------------------------------------------------------------------
# بنك الحوارات: كل سؤال عنده خيارات، وحد منها "مريب" (يميل يفضح خبرة طبية
# أو هدوء غريب بالأزمات). اللاعب اللي يختار الجواب المريب يزيد "درجة شكه"
# عند القاتل بدون ما يدري إن جوابه كان مريب.
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "q": "💬 أحد اللاعبين انخدش وهو يلعب، شتسوي؟",
        "options": [
            ("أتجاهله، مو مشكلتي 🤷", False),
            ("أشوف حاله بس من بعيد", False),
            ("خليه علي، أعرف بالضبط شلون أعالجه 🩹", True),
        ],
    },
    {
        "q": "💬 لو صار موقف طارئ فجأة بالمجموعة، شنو أول رد فعل لك؟",
        "options": [
            ("أصيح أدور أي وحد يعرف إسعافات أولية", False),
            ("أتجمد من الخوف، ما أدري شسوي 😨", False),
            ("أفحص الوضع بسرعة وأتصرف بهدوء", True),
        ],
    },
    {
        "q": "💬 ليش تبدو هادئ بهاي الأجواء المتوترة؟",
        "options": [
            ("لأني معتاد أضبط أعصابي بالأزمات", True),
            ("والله أنا خايف مثل الكل", False),
            ("بس حاب أضحك على الموقف مو أكثر 😂", False),
        ],
    },
    {
        "q": "💬 لو تعرف إن أحد بالمجموعة يخفي شي، شسوي؟",
        "options": [
            ("أراقبه بصمت وأنتظر", False),
            ("أسأله على طول بدون مجاملة", False),
            ("أحاول أكسب ثقته أول، هذا أسلوبي دايمًا 🎭", True),
        ],
    },
    {
        "q": "💬 شنو أكثر شي يخليك تحس بالراحة بلعبة زي هذي؟",
        "options": [
            ("لما الكل يضحك ويرفه عن نفسه", False),
            ("لما أعرف إني أقدر أساعد لو صار شي 🩺", True),
            ("لما ألعب بهدوء بدون ضغط", False),
        ],
    },
    {
        "q": "💬 لو طلب منك أحد مساعدة مستعجلة، شعورك؟",
        "options": [
            ("متردد شوي، ما أدري أقدر أساعد لو لا", False),
            ("متحمس، أحب أكون المسؤول عن مساعدة الناس", True),
            ("أحيله لشخص ثاني أقدر منه", False),
        ],
    },
]


class Game:
    """يمثل جلسة لعبة واحدة داخل مجموعة معيّنة."""

    def __init__(self, owner_id, chat_id):
        self.owner = owner_id
        self.chat_id = chat_id
        self.players = {}          # user_id -> {"name": str}
        self.started = False       # يمنع تشغيل اللعبة مرتين بالتوازي

        self.killer = None         # يُختار مرة وحدة، ثابت طوال اللعبة
        self.doctor = None         # يُختار مرة وحدة، ما يتعوض إذا مات
        self.detective = None      # NEW: دور المحقق، يحقق سري بلاعب كل جولة
        self.protected = None      # اللاعب المحمي بالجولة الحالية
        self.last_protected = None  # NEW: آخر شخص حماه الطبيب فعليًا (يمنع تكرار نفس الحماية جولتين على التوالي)

        self.killer_event = asyncio.Event()
        self.doctor_event = asyncio.Event()
        self.detective_event = asyncio.Event()   # NEW

        self.current_question = None
        self.answered_this_round = set()
        self.suspect_score = {}    # user_id -> عدد مرات جاوب جواب مريب

        # FIX #2: قفل ضد الضغط المزدوج على أزرار القاتل بنفس الجولة
        self.kill_action_done = False

        # NEW: تصويت النهار العلني — كل اللاعبين يشاركون فيه
        self.votes = {}            # voter_id -> target_id (أو None لو امتنع)
        self.voting_open = False

        # يحتفظ بأسماء كل من دخل اللعبة (حتى بعد موتهم) عشان نقدر نكشف
        # الأدوار بنهاية اللعبة بدون ما نفقد الاسم.
        self.name_history = {}

    # ---- إدارة اللاعبين ----
    def add_player(self, user_id, name):
        self.players[user_id] = {"name": name}
        self.name_history[user_id] = name

    def remove_player(self, user_id):
        removed = self.players.pop(user_id, None)
        # FIX #1: لو اللاعب المحمي هو نفسه اللي انحذف (مات)، صفّر الحماية
        # حتى ما تبقى "عالقة" على شخص خرج من اللعبة.
        if removed is not None and self.protected == user_id:
            self.protected = None
        # FIX #1 (تكملة): لو الطبيب نفسه هو اللي مات، صفّر الحماية فورًا
        # عشان ما تضل قيمة قديمة تحصّن لاعب طول باقي اللعبة بدون داعي.
        if removed is not None and user_id == self.doctor:
            self.protected = None
        return removed

    def is_player(self, user_id):
        return user_id in self.players

    # ---- إدارة الأدوار (تُحدد مرة وحدة فقط) ----
    def assign_roles(self):
        ids = list(self.players.keys())
        self.killer = random.choice(ids)
        remaining = [i for i in ids if i != self.killer]
        self.doctor = random.choice(remaining) if remaining else None

        # NEW: دور المحقق يُفعّل فقط لو عدد اللاعبين 4 أو أكثر، حتى يبقى
        # فيه على الأقل مواطن عادي غير الأدوار الخاصة الثلاثة.
        remaining2 = [i for i in remaining if i != self.doctor]
        if len(ids) >= 4 and remaining2:
            self.detective = random.choice(remaining2)
        else:
            self.detective = None

    def killer_alive(self):
        return self.killer is not None and self.killer in self.players

    def doctor_alive(self):
        return self.doctor is not None and self.doctor in self.players

    def detective_alive(self):
        return self.detective is not None and self.detective in self.players

    def set_protected(self, user_id):
        self.protected = user_id
        self.doctor_event.set()

    def end(self):
        self.players.clear()
        self.killer = None
        self.doctor = None
        self.detective = None
        self.protected = None
        self.last_protected = None
        self.votes = {}
        self.voting_open = False
        self.killer_event.set()
        self.doctor_event.set()
        self.detective_event.set()


games = {}  # chat_id -> Game


def end_game(chat_id):
    """تنهي اللعبة وتحذفها من القاموس العام حتى يمكن بدء لعبة جديدة."""
    game = games.pop(chat_id, None)
    if game:
        game.end()


async def announce(game, text):
    """يرسل رسالة علنية بمجموعة اللعبة (يُستخدم من داخل محادثات خاصة)."""
    try:
        await ABH.send_message(game.chat_id, text)
    except Exception:
        pass


def check_winner(game):
    """
    NEW: يتحقق من شروط الفوز بعد أي إزالة لاعب (تصويت أو قتل ليلي).
    يرجع (انتهت_اللعبة, نوع_الفائز) حيث نوع_الفائز هي "village" أو "killer".
    """
    if not game.killer_alive():
        return True, "village"
    # قاعدة كلاسيكية: لو تبقى القاتل ولاعب واحد بس معاه، القاتل يفوز حتمًا
    # بالجولة الجاية، فنعتبره فايز من الحين.
    if len(game.players) <= 2:
        return True, "killer"
    return False, None


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
    await e.reply(f"تم تشغيل لعبة القاتل والمقتول 🎭\nانت مالك اللعبة ( {m} )", buttons=[b])

    game = Game(user, chat)
    game.add_player(user, m)
    games[chat] = game


@ABH.on(events.NewMessage(pattern=r'^/start killamorder_(-?[0-9]+)$'))
async def join_game(e):
    chat_id = int(e.pattern_match.group(1))
    game = games.get(chat_id)
    if not game:
        return await e.reply("لا توجد لعبة شغالة في هذه المجموعة")
    if game.started:
        return await e.reply("اللعبة بدأت بالفعل، انتظر جولة جديدة")
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
    lines = [f'• {p["name"]}' for p in game.players.values()]
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
    game.assign_roles()

    try:
        await ABH.send_message(
            game.killer,
            "🔪 أنت القاتل السري بهذي اللعبة!\n"
            "دورك ثابت طول اللعبة. كل جولة (بالليل) راح أرسلك هني خيارات لتحديد ضحيتك بالخفاء.\n"
            "🕵️ راقب إجابات الحوارات العامة بعناية... يمكن تساعدك تكتشف مين الطبيب!\n"
            "⚖️ احذر! باقي اللاعبين يصوتون علنًا كل جولة على مين يشكون فيه، فلازم تمثل دور البريء بذكاء."
        )
    except Exception:
        pass

    if game.doctor:
        try:
            await ABH.send_message(
                game.doctor,
                "🩺 أنت الطبيب السري بهذي اللعبة!\n"
                "كل جولة اختار مين تحمي من هني بالخاص.\n"
                "⚠️ انتبه: ما تكدر تحمي نفس الشخص جولتين متتاليتين، خطط بذكاء!\n"
                "⚠️ انتبه لإجاباتك بالحوارات العامة، القاتل يراقب من يجاوب بإجابات تفضح خبرة طبية!"
            )
        except Exception:
            pass

    if game.detective:
        try:
            await ABH.send_message(
                game.detective,
                "🕵️ أنت المحقق السري بهذي اللعبة!\n"
                "كل جولة تقدر تحقق سري بلاعب وحد من هني بالخاص، وراح أخبرك هل هو القاتل أو بريء.\n"
                "استخدم معلوماتك بذكاء وقت التصويت العلني عشان توجه المجموعة للشخص الصح... بدون ما تفضح نفسك!"
            )
        except Exception:
            pass

    await e.reply(
        "🎭 يتم بدء اللعبة ... كل لاعب عنده دور سري، والحوار الأول جاي!\n"
        "بعد كل حوار راح يصير تصويت علني — كل اللاعبين يشاركون فيه لتحديد المشكوك فيه!"
    )

    winner_type = None

    while chat in games and len(games[chat].players) > 1:
        game = games[chat]

        # ---------------- جولة الحوار العلنية (يشارك فيها الجميع) ----------------
        await run_dialogue_round(e, game)
        if chat not in games:
            break
        game = games[chat]

        # ---------------- NEW: التصويت النهاري العلني (يشارك فيه الجميع) --------
        await run_day_vote(e, game)
        if chat not in games:
            break
        game = games[chat]

        over, winner_type = check_winner(game)
        if over:
            break

        # ---------------- الليل: الطبيب يحمي ----------------
        if game.doctor_alive():
            await ask_doctor_protect(game)
            game.doctor_event.clear()
            try:
                await asyncio.wait_for(game.doctor_event.wait(), timeout=20)
            except asyncio.TimeoutError:
                game.protected = None  # الطبيب ما تصرف بالوقت
        else:
            # FIX #1: لو الطبيب ميت أصلاً، تأكد ما فيه حماية عالقة من جولة سابقة
            game.protected = None

        # ---------------- NEW: الليل: المحقق يحقق ----------------
        if game.detective_alive():
            game.detective_event.clear()
            await ask_detective_investigate(game)
            try:
                await asyncio.wait_for(game.detective_event.wait(), timeout=20)
            except asyncio.TimeoutError:
                pass  # المحقق ما تصرف بالوقت، يفوت هالجولة بدون معلومة

        if not game.killer_alive():
            over, winner_type = check_winner(game)
            break

        # ---------------- الليل: القاتل يتحرك ----------------
        # FIX #2: افتح جولة قتل جديدة وصفّر القفل قبل إرسال الأزرار
        game.kill_action_done = False
        await ask_killer_to_act(game)
        game.killer_event.clear()
        try:
            await asyncio.wait_for(game.killer_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            await announce(game, "⏳ مرّ الوقت والقاتل ما تحرك هالجولة... يبدو متردد 👀")
        finally:
            # FIX #2: أغلق نافذة القتل بعد انتهاء الجولة بأي طريقة (نجاح أو تايم أوت)
            game.kill_action_done = True

        game = games.get(chat)
        if not game:
            break

        over, winner_type = check_winner(game)
        if over:
            break

        await asyncio.sleep(random.randint(3, 6))

    game = games.get(chat)
    if not game:
        return  # اللعبة انهت يدويًا بالنص، ما فيه شي نعلنه

    if winner_type is None:
        # احتياطي: الحلقة خرجت لأن عدد اللاعبين وصل لـ 1 بدون ما يمر على check_winner
        winner_type = "killer" if game.killer_alive() else "village"

    killer_name = game.name_history.get(game.killer, "غير معروف")
    doctor_name = game.name_history.get(game.doctor, "لا يوجد") if game.doctor else "لا يوجد"
    detective_name = game.name_history.get(game.detective, "لا يوجد") if game.detective else "لا يوجد"

    reveal = (
        f"🔪 القاتل كان: {killer_name}\n"
        f"🩺 الطبيب كان: {doctor_name}\n"
        f"🕵️ المحقق كان: {detective_name}"
    )

    if winner_type == "killer":
        await e.reply(f"🔪 فاز القاتل! نجح يتخلص من أغلب اللاعبين بالخفاء.\n\n{reveal}")
    else:
        await e.reply(f"🎉 فاز الأبرياء! تم كشف القاتل قبل ما يفوز.\n\n{reveal}")

    end_game(chat)


# ---------------------------------------------------------------------------
# جولة الحوار العلنية
# ---------------------------------------------------------------------------

async def run_dialogue_round(e, game):
    game.current_question = random.choice(QUESTIONS)
    game.answered_this_round = set()

    btns = [[Button.inline(text, data=f"answer:{i}")]
            for i, (text, _) in enumerate(game.current_question["options"])]
    await e.reply(game.current_question["q"], buttons=btns)

    await asyncio.sleep(15)  # وقت للاعبين يجاوبون
    game.current_question = None

    if game.killer_alive():
        await send_suspect_hint(game)


async def send_suspect_hint(game):
    if not game.suspect_score:
        try:
            await ABH.send_message(game.killer, "🕵️ لسا ما لاحظت أي إجابة مريبة من أحد...")
        except Exception:
            pass
        return

    ranked = sorted(game.suspect_score.items(), key=lambda x: x[1], reverse=True)[:3]
    lines = []
    for uid, score in ranked:
        pdata = game.players.get(uid)
        if pdata:
            lines.append(f"• {pdata['name']} — جاوب بشكل مريب {score} مرة/مرات")
    if lines:
        msg = "🕵️ حسب الحوارات، هذولا أكثر لاعبين يثيرون الشك:\n" + "\n".join(lines)
        try:
            await ABH.send_message(game.killer, msg)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# NEW: التصويت النهاري العلني — كل اللاعبين (مو بس القاتل والطبيب) يشاركون
# فعليًا بمصير اللعبة، ويصوتون على مين يشكون فيه بناءً على إجاباته وسلوكه.
# ---------------------------------------------------------------------------

async def run_day_vote(e, game):
    if len(game.players) < 3:
        # التصويت يحتاج 3 لاعبين على الأقل عشان يكون له معنى فعلي
        return

    game.votes = {}
    game.voting_open = True

    btns = [[Button.inline(p["name"], data=f"vote:{uid}")]
            for uid, p in game.players.items()]
    btns.append([Button.inline("🤷 امتناع عن التصويت", data="vote_skip")])
    await e.reply(
        "⚖️ حان وقت التصويت العلني! ناقشوا وقرروا مين تشكون فيه...\n"
        "(كل اللاعبين يصوتون، عندكم 25 ثانية)",
        buttons=btns,
    )

    await asyncio.sleep(25)
    game.voting_open = False

    tally = {}
    for target in game.votes.values():
        if target is None:
            continue
        tally[target] = tally.get(target, 0) + 1

    if not tally:
        await e.reply("🤷 محد صوّت (أو الكل امتنع)، ما راح يُطرد أحد هالجولة.")
        return

    max_votes = max(tally.values())
    top = [uid for uid, v in tally.items() if v == max_votes]

    if len(top) > 1:
        await e.reply("⚖️ الأصوات متعادلة بين أكثر من لاعب، محد راح يُطرد هالجولة.")
        return

    victim_id = top[0]
    victim = game.players.get(victim_id)
    if not victim:
        return

    was_killer = victim_id == game.killer
    victim_name = victim["name"]
    game.remove_player(victim_id)

    if was_killer:
        await e.reply(
            f"⚖️ صوتت المجموعة على طرد ( {victim_name} ) بـ {max_votes} صوت...\n"
            f"🔪🎉 وطلع هو القاتل السري! فاز الأبرياء!"
        )
    else:
        await e.reply(
            f"⚖️ صوتت المجموعة على طرد ( {victim_name} ) بـ {max_votes} صوت...\n"
            f"😢 بس طلع بريء! القاتل الحقيقي لسا بينكم..."
        )


@ABH.on(events.CallbackQuery(pattern=r"vote:(\d+)|vote_skip"))
async def vote_callback(e):
    game = games.get(e.chat_id)
    if not game or not game.voting_open:
        return await e.answer("لا يوجد تصويت نشط حاليًا", alert=True)
    if not game.is_player(e.sender_id):
        return await e.answer("أنت لست داخل اللعبة", alert=True)

    data = e.data.decode()
    if data == "vote_skip":
        game.votes[e.sender_id] = None
        return await e.answer("تم تسجيل امتناعك ✅")

    target_id = int(data.split(":")[1])
    if target_id not in game.players:
        return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)
    if target_id == e.sender_id:
        return await e.answer("ما تكدر تصوت لنفسك 😅", alert=True)

    game.votes[e.sender_id] = target_id
    await e.answer("تم تسجيل صوتك ✅ (تكدر تغيّره لين ما ينتهي الوقت)")


@ABH.on(events.CallbackQuery(pattern=r"answer:(\d+)"))
async def answer_callback(e):
    game = games.get(e.chat_id)
    if not game or not game.current_question:
        return await e.answer("لا يوجد سؤال نشط حاليًا", alert=True)
    if not game.is_player(e.sender_id):
        return await e.answer("أنت لست داخل اللعبة", alert=True)
    if e.sender_id in game.answered_this_round:
        return await e.answer("جاوبت على هالسؤال بالفعل", alert=True)

    idx = int(e.pattern_match.group(1))
    options = game.current_question["options"]
    if idx >= len(options):
        return await e.answer("خيار غير صالح", alert=True)

    game.answered_this_round.add(e.sender_id)
    _, is_suspicious = options[idx]
    if is_suspicious:
        game.suspect_score[e.sender_id] = game.suspect_score.get(e.sender_id, 0) + 1

    await e.answer("تم تسجيل جوابك ✅")


# ---------------------------------------------------------------------------
# دور الطبيب (خاص وسري)
# ---------------------------------------------------------------------------

async def ask_doctor_protect(game):
    btns = [[Button.inline(p["name"], data=f"protect:{uid}")]
            for uid, p in game.players.items()]
    btns.append([Button.inline("بدون حماية هالجولة", data="protect_skip")])
    try:
        await ABH.send_message(game.doctor, "🩺 مين تريد تحمي هالجولة؟ (عندك 20 ثانية)", buttons=btns)
    except Exception:
        game.protected = None  # ما كدرنا نوصله، اللعبة تكمل بدون حماية


@ABH.on(events.CallbackQuery(pattern=r"protect:(\d+)|protect_skip"))
async def doctor_callback(e):
    game = next((g for g in games.values() if g.doctor == e.sender_id and g.doctor_alive()), None)
    if not game:
        return await e.answer("لا توجد لعبة نشطة لك كطبيب حاليًا", alert=True)

    data = e.data.decode()
    if data == "protect_skip":
        game.last_protected = None
        game.set_protected(None)
        return await e.edit("تمام، ما راح تحمي أحد هالجولة")

    target_id = int(data.split(":")[1])
    if target_id not in game.players:
        return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)

    # NEW: قاعدة كلاسيكية — ما تقدر تحمي نفس الشخص جولتين على التوالي
    if target_id == game.last_protected:
        return await e.answer("ما تكدر تحمي نفس الشخص جولتين متتاليتين! اختر غيره 🩺", alert=True)

    game.last_protected = target_id
    game.set_protected(target_id)
    target_name = game.players[target_id]["name"]
    await e.edit(f"تمام، راح تحمي ( {target_name} ) هالجولة")


async def ask_killer_to_act(game):
    btns = [
        Button.inline("تحديد الضحية", data="choice_to_kill"),
        Button.inline("قتل عشوائي", data="autokill"),
    ]
    try:
        await ABH.send_message(game.killer, "🔪 حان وقت التحرك... اختر نوع القتل هالجولة (30 ثانية)", buttons=btns)
    except Exception:
        pass


@ABH.on(events.CallbackQuery(pattern=r"choice_to_kill|autokill|kill:(\d+)"))
async def kill_callback(e):
    game = next((g for g in games.values() if g.killer == e.sender_id and g.killer_alive()), None)
    if not game:
        return await e.answer("لا توجد لعبة نشطة لك كقاتل حاليًا", alert=True)

    data = e.data.decode()

    # "تحديد الضحية" مجرد فتح قائمة اختيار، مو فعل قتل فعلي، فما يلزم قفل
    if data == "choice_to_kill":
        btns = [[Button.inline(p["name"], data=f"kill:{uid}")]
                for uid, p in game.players.items() if uid != game.killer]
        if not btns:
            return await e.answer("لا يوجد لاعبين آخرين", alert=True)
        return await e.edit("اختر الضحية:", buttons=btns)

    # FIX #2: أي فعل قتل فعلي (autokill أو kill:ID) يمر من هنا، ونقفله بعد أول تنفيذ
    if game.kill_action_done:
        return await e.answer("خلصت هالجولة بالفعل، ما تكدر تقتل مرتين!", alert=True)
    game.kill_action_done = True

    players = game.players
    killer = game.killer

    if data == "autokill":
        candidates = {uid: p for uid, p in players.items() if uid != killer}
        if not candidates:
            game.kill_action_done = False  # ما صار فعل فعلي، رجّع القفل
            return await e.edit("لا يوجد لاعبين آخرين لقتلهم")
        victim_id, victim = random.choice(list(candidates.items()))
        if victim_id == game.protected:
            game.protected = None
            await e.edit(f"حاولت تقتل ( {victim['name']} ) بس الطبيب أنقذه! 🩺")
            await announce(game, "🩺 حاول القاتل يضرب الليلة... بس حد أنقذ الضحية بالوقت المناسب!")
        else:
            game.remove_player(victim_id)
            await e.edit(f"تم قتل ( {victim['name']} )")
            await announce(game, f"💀 تم العثور على ( {victim['name']} ) مقتولاً!")
        game.killer_event.set()
        return

    if data.startswith("kill:"):
        victim_id = int(data.split(":")[1])
        if victim_id not in players:
            game.kill_action_done = False  # ما صار فعل فعلي، رجّع القفل
            return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)
        victim_name = players[victim_id]["name"]
        if victim_id == game.protected:
            game.protected = None
            await e.edit(f"حاولت تقتل ( {victim_name} ) بس الطبيب أنقذه! 🩺")
            await announce(game, "🩺 حاول القاتل يضرب الليلة... بس حد أنقذ الضحية بالوقت المناسب!")
        else:
            game.remove_player(victim_id)
            await e.edit(f"تم قتل ( {victim_name} ) بنجاح")
            await announce(game, f"💀 تم العثور على ( {victim_name} ) مقتولاً!")
        game.killer_event.set()
        return


# ---------------------------------------------------------------------------
# NEW: دور المحقق (خاص وسري) — يحقق بلاعب وحد كل جولة ويعرف هل هو القاتل
# ---------------------------------------------------------------------------

async def ask_detective_investigate(game):
    btns = [[Button.inline(p["name"], data=f"investigate:{uid}")]
            for uid, p in game.players.items() if uid != game.detective]
    if not btns:
        return
    try:
        await ABH.send_message(
            game.detective,
            "🕵️ مين تريد تحقق فيه هالجولة؟ (عندك 20 ثانية)",
            buttons=btns,
        )
    except Exception:
        pass


@ABH.on(events.CallbackQuery(pattern=r"investigate:(\d+)"))
async def detective_callback(e):
    game = next((g for g in games.values() if g.detective == e.sender_id and g.detective_alive()), None)
    if not game:
        return await e.answer("لا توجد لعبة نشطة لك كمحقق حاليًا", alert=True)

    target_id = int(e.pattern_match.group(1))
    if target_id not in game.players:
        return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)

    target_name = game.players[target_id]["name"]
    if target_id == game.killer:
        result = f"🔪 نتيجة التحقيق: ( {target_name} ) هو القاتل السري! استخدم هالمعلومة بذكاء وقت التصويت."
    else:
        result = f"✅ نتيجة التحقيق: ( {target_name} ) بريء، مو القاتل."

    await e.edit(result)
    game.detective_event.set()
