from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio


class Game:
    def __init__(self, owner_id):
        self.owner = owner_id
        self.players = {}
        self.current_killer = None

    def add_player(self, user_id, name):
        self.players[user_id] = {"name": name, "points": 2}

    def player(self, id):
        return self.players[id]

    def remove_player(self, user_id):
        return self.players.pop(user_id, None)

    def end(self):
        self.players.clear()
        self.current_killer = None

    def is_player(self, user_id):
        return user_id in self.players

    def set_killer(self, id):
        self.current_killer = id

    def get_killer(self):
        return self.current_killer

    def del_killer(self):
        self.current_killer = None


killamorder = {}


def end_game(chat_id):
    """تنهي اللعبة وتحذفها من القاموس العام حتى يمكن بدء لعبة جديدة"""
    game = killamorder.pop(chat_id, None)
    if game:
        game.end()


@ABH.on(events.NewMessage(pattern='(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    user = e.sender_id
    if chat in killamorder:
        return await e.reply("اللعبة قيد التشغيل بالفعل")
    m = await mention(e)
    my = await ABH.get_me()
    b = Button.url('اضغط هنا للانضمام', url=f"https://t.me/{my.username}?start=killamorder_{chat}")
    await e.reply(f"تم تشغيل لعبة القاتل والمقتول \n انت مالك اللعبة ( {m} )", buttons=[b])
    game = Game(user)
    killamorder[chat] = game
    game.add_player(user, m)


@ABH.on(events.NewMessage(pattern=r'/start killamorder_(-?[0-9]+)$'))
async def join_game(e):
    chat_id = int(e.pattern_match.group(1))
    if chat_id not in killamorder:
        return await e.reply("لا توجد لعبة شغالة في هذه المجموعة")
    game = killamorder[chat_id]
    if game.is_player(e.sender_id):
        return await e.reply("أنت بالفعل داخل اللعبة!")
    m = await mention(e)
    game.add_player(e.sender_id, m)
    await e.reply(f"تم إضافتك للعبة بنجاح! عدد اللاعبين الآن: {len(game.players)}")


@ABH.on(events.NewMessage(pattern='اللاعبين'))
async def show_players(e):
    chat = e.chat_id
    if chat not in killamorder:
        return
    game = killamorder[chat]
    msg = "اللاعبين:\n"
    for _, pdata in game.players.items():
        الاعب = pdata["name"]
        نقاطة = pdata["points"]
        msg += f'{الاعب}  -  {نقاطة}\n'
    await e.reply(msg)


@ABH.on(events.NewMessage(pattern='تم', incoming=True))
async def start_game(e):
    chat = e.chat_id
    game = killamorder.get(chat)
    if not game:
        return
    if e.sender_id != game.owner:
        return await e.reply("أنت لست مالك اللعبة")

    if len(game.players) < 2:
        return await e.reply("لازم لاعبين اثنين على الأقل عشان تبدأ اللعبة")

    await e.reply("يتم بدء اللعبة ...")

    # اللعبة تستمر لحد ما يبقى لاعب واحد أو أقل، بدل عدد ثابت من الجولات
    while chat in killamorder and len(killamorder[chat].players) > 1:
        await set_auto_killer(e)
        game = killamorder.get(chat)
        if not game:
            break
        waited = 0
        while game.get_killer() is not None and waited < 30:
            await asyncio.sleep(1)
            waited += 1
        await asyncio.sleep(random.randint(3, 6))


async def set_auto_killer(e):
    chat = e.chat_id
    game = killamorder.get(chat)
    if not game:
        return
    players = game.players

    if not players:
        end_game(chat)
        return

    if len(players) == 1:
        winner_id = next(iter(players))
        winner = players[winner_id]
        اسمه = winner["name"]
        محاولاته = winner["points"]
        await e.reply(f"🎉 مبارك للاعب ( {اسمه} ) - محاولاته المتبقية: {محاولاته}")
        end_game(chat)
        return

    player_id, pdata = random.choice(list(players.items()))
    killer_name = pdata["name"]
    points = pdata["points"]

    if points <= 0:
        await e.reply(f"الله يرحمك ( {killer_name} ) — ماتت نقاطك")
        game.remove_player(player_id)
        return

    game.set_killer(player_id)
    btns = [
        Button.inline("تحديد الضحية", data="choice_to_kill"),
        Button.inline("قتل عشوائي", data="autokill"),
    ]
    await e.reply(f"أنت القاتل يا ( {killer_name} ) — اختر نوع القتل", buttons=btns)
    game.players[player_id]["points"] -= 1


@ABH.on(events.CallbackQuery(pattern=r"choice_to_kill|autokill|kill:(\d+)"))
async def kill_callback(e):
    chat = e.chat_id
    game = killamorder.get(chat)
    if not game:
        await e.answer("لا توجد لعبة نشطة", alert=True)
        return

    killer = game.get_killer()
    if not killer or e.sender_id != killer:
        await e.answer("أنت لست القاتل!", alert=True)
        return

    data = e.data.decode()
    players = game.players

    if data == "autokill":
        candidates = {uid: pdata for uid, pdata in players.items() if uid != killer}
        if not candidates:
            game.del_killer()
            await e.edit("لا يوجد لاعبين آخرين لقتلهم")
            return
        victim_id, victim_data = random.choice(list(candidates.items()))
        game.del_killer()
        await e.edit(f"تم قتل اللاعب ( {victim_data['name']} )")
        game.remove_player(victim_id)
        return

    elif data == "choice_to_kill":
        txt = "اختر الضحية:\n"
        btns = []
        for uid, pdata in players.items():
            if uid != killer:
                btns.append([Button.inline(pdata["name"], data=f"kill:{uid}")])
        if not btns:
            await e.answer("لا يوجد لاعبين آخرين", alert=True)
            return
        await e.edit(txt, buttons=btns)
        return

    if data.startswith("kill:"):
        victim_id = int(data.split(":")[1])
        if victim_id not in players:
            await e.answer("هذا اللاعب غير موجود بعد الآن", alert=True)
            return
        game.del_killer()
        victim = players[victim_id]["name"]
        game.remove_player(victim_id)
        await e.edit(f"تم قتل ( {victim} ) بنجاح")
        return
