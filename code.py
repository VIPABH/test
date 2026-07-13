from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio
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
            ("أدور أي وحد يعرف إسعافات أولية", False),
            ("صراحة أتجمد من الخوف، ما أدري شسوي 😨", False),
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
        "q": "💬 شنو أكثر شي يخليك تحس بالراحة ب لعبة مثل هاي؟",
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
    def __init__(self, owner_id, chat_id):
        self.owner = owner_id
        self.chat_id = chat_id
        self.players = {}
        self.started = False
        self.killer = None
        self.doctor = None
        self.protected = None
        self.killer_event = asyncio.Event()
        self.doctor_event = asyncio.Event()
        self.current_question = None
        self.answered_this_round = set()
        self.suspect_score = {}
        self.kill_action_done = False
        self.name_history = {}
    def add_player(self, user_id, name):
        self.players[user_id] = {"name": name}
        self.name_history[user_id] = name
    def remove_player(self, user_id):
        removed = self.players.pop(user_id, None)
        if removed is not None and self.protected == user_id:
            self.protected = None
        if removed is not None and user_id == self.doctor:
            self.protected = None
        return removed
    def is_player(self, user_id):
        return user_id in self.players
    def assign_roles(self):
        ids = list(self.players.keys())
        self.killer = random.choice(ids)
        remaining = [i for i in ids if i != self.killer]
        self.doctor = random.choice(remaining) if remaining else None
    def killer_alive(self):
        return self.killer is not None and self.killer in self.players
    def doctor_alive(self):
        return self.doctor is not None and self.doctor in self.players
    def set_protected(self, user_id):
        self.protected = user_id
        self.doctor_event.set()
    def end(self):
        self.players.clear()
        self.killer = None
        self.doctor = None
        self.protected = None
        self.killer_event.set()
        self.doctor_event.set()
games = {}
def end_game(chat_id):
    game = games.pop(chat_id, None)
    if game:
        game.end()
async def announce(game, text):
    try:
        await ABH.send_message(game.chat_id, text)
    except Exception:
        pass
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
    game = games.get(e.chat_id)
    if not game or game.started:
        return
    if not game.is_player(e.sender_id):
        return await e.reply("أنت لست داخل اللعبة")
    game.remove_player(e.sender_id)
    await e.reply("تم انسحابك من اللعبة")
@ABH.on(events.NewMessage(pattern='^(/endgame|إنهاء اللعبة)$'))
async def force_end_game(e):
    game = games.get(e.chat_id)
    if not game:
        return await e.reply("لا توجد لعبة شغالة")
    if e.sender_id != game.owner:
        return await e.reply("بس مالك اللعبة يكدر ينهيها")
    end_game(e.chat_id)
    await e.reply("تم إنهاء اللعبة")
@ABH.on(events.NewMessage(pattern='^تم$'))
async def start_game(e):
    chat = e.chat_id
    game = games.get(chat)
    if not game:
        return
    if e.sender_id != game.owner:
        return await e.reply("أنت لست مالك اللعبة")
    if game.started:
        return
    if len(game.players) < 2:
        return await e.reply("لازم لاعبين اثنين على الأقل عشان تبدأ اللعبة")
    game.started = True
    game.assign_roles()
    try:
        await ABH.send_message(
            game.killer,
            "🔪 أنت القاتل السري بهذي اللعبة!\n"
            "دورك ثابت طول اللعبة. كل جولة راح أرسلك هني خيارات لتحديد ضحيتك بالخفاء.\n"
            "🕵️ راقب إجابات الحوارات العامة بعناية... يمكن تساعدك تكتشف مين الطبيب!"
        )
    except Exception:
        pass
    if game.doctor:
        try:
            await ABH.send_message(
                game.doctor,
                "🩺 أنت الطبيب السري بهذي اللعبة!\n"
                "كل جولة اختار مين تحمي منا بالخاص.\n"
                "⚠️ انتبه لإجاباتك بالحوارات العامة، القاتل يراقب من يجاوب بإجابات تفضح خبرة طبية!"
            )
        except Exception:
            pass
    await e.reply("🎭 يتم بدء اللعبة ... كل لاعب عنده دور سري، والحوار الأول جاي!")
    while chat in games and len(games[chat].players) > 1:
        game = games[chat]
        await run_dialogue_round(e, game)
        if chat not in games:
            break
        game = games[chat]
        if game.doctor_alive():
            await ask_doctor_protect(game)
            game.doctor_event.clear()
            try:
                await asyncio.wait_for(game.doctor_event.wait(), timeout=20)
            except asyncio.TimeoutError:
                game.protected = None
        else:
            game.protected = None
        if not game.killer_alive():
            break
        game.kill_action_done = False
        await ask_killer_to_act(game)
        game.killer_event.clear()
        try:
            await asyncio.wait_for(game.killer_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            await announce(game, "⏳ مرّ الوقت والقاتل ما تحرك هالجولة... يبدو متردد 👀")
        finally:
            game.kill_action_done = True
        await asyncio.sleep(random.randint(3, 6))
    game = games.get(chat)
    if game and len(game.players) == 1:
        winner_id, winner = next(iter(game.players.items()))
        if winner_id == game.killer:
            await e.reply(f"🏆 الفائز هو ( {winner['name']} ) ... وكان هو القاتل السري طوال اللعبة! 🔪")
        else:
            killer_name = game.name_history.get(game.killer, "غير معروف")
            doctor_name = game.name_history.get(game.doctor, "لا يوجد") if game.doctor else "لا يوجد"
            await e.reply(
                f"🎉 مبارك للفائز ( {winner['name']} )!\n"
                f"🔪 القاتل السري كان: {killer_name}\n"
                f"🩺 الطبيب السري كان: {doctor_name}"
            )
        end_game(chat)
async def run_dialogue_round(e, game):
    game.current_question = random.choice(QUESTIONS)
    game.answered_this_round = set()
    btns = [[Button.inline(text, data=f"answer:{i}")]
            for i, (text, _) in enumerate(game.current_question["options"])]
    await e.reply(game.current_question["q"], buttons=btns)
    await asyncio.sleep(15)
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
        game.set_protected(None)
        return await e.edit("تمام، ما راح تحمي أحد هالجولة")
    target_id = int(data.split(":")[1])
    if target_id not in game.players:
        return await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)
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
    if data == "choice_to_kill":
        btns = [[Button.inline(p["name"], data=f"kill:{uid}")]
                for uid, p in game.players.items() if uid != game.killer]
        if not btns:
            return await e.answer("لا يوجد لاعبين آخرين", alert=True)
        return await e.edit("اختر الضحية:", buttons=btns)
    if game.kill_action_done:
        return await e.answer("خلصت هالجولة بالفعل، ما تكدر تقتل مرتين!", alert=True)
    game.kill_action_done = True
    players = game.players
    killer = game.killer
    if data == "autokill":
        candidates = {uid: p for uid, p in players.items() if uid != killer}
        if not candidates:
            game.kill_action_done = False
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
            game.kill_action_done = False
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
