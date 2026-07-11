from telethon import events, Button
from Resources import mention
from ABH import ABH
import random, asyncio
class Game:
    def __init__(self, owner_id):
        self.owner = owner_id
        self.players = {} 
    def add_player(self, user_id, name):
        self.players[user_id] = {"name": name, "points": 2}
    def player(self, id):
        return self.players[id]
    def remove_player(self, user_id):
        return self.players.pop(user_id, None)
    def end(self):
        return self.players.clear()
    def is_player(self, user_id):
        return user_id in self.players
    def killer(self, id=None):
        if id is None:
            return self.killer
        self.killer = id
    def del_killer(self):
        self.killer = None
killamorder = {}
@ABH.on(events.NewMessage(pattern='(/killamorder|القاتل والمقتول)$'))
async def killamorderstart(e):
    chat = e.chat_id
    user = e.sender_id
    if chat in killamorder:
        return await e.reply("اللعبة قيد التشغيل بالفعل")
    m = await mention(e)
    my = await ABH.get_me()
    b = Button.url('اضغط هنا للانضمام', url=f"https://t.me/{my.username}?start=killamorder:{chat}")
    msg = await e.reply(f"تم تشغيل لعبة القاتل والمقتول \n انت مالك اللعبة ( {m} )", buttons=[b])
    game = Game(user)
    killamorder[chat] = game
    game.add_player(user, m)
@ABH.on(events.NewMessage(pattern='killamorder:([0-9]+)$'))
async def start_game(e):
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
        return await e.reply("لا توجد لعبة شغالة")
    game = killamorder[chat]
    msg = "اللاعبين:\n"
    for _, pdata in game.players.items():
        الاعب = pdata["name"]
        نقاطة = pdata["points"]
        msg+= f'{الاعب=}  -  {نقاطة=}\n'
    await e.reply(msg)
@ABH.on(events.NewMessage(pattern='تم', incoming=True))
async def start_game(e):
    chat = e.chat_id
    game = killamorder.get(chat)
    if not game:return
    if e.sender_id != game.owner:
        return await e.reply("أنت لست مالك اللعبة")
    await e.reply("يتم بدء اللعبة ...")
    players_count = len(game.players) * 2
    for _ in range(players_count):
        await set_auto_killer(e)
        await asyncio.sleep(random.randint(6, 12))
async def set_auto_killer(e):
    chat = e.chat_id
    game = killamorder[chat]
    players = game.players
    if not players:
        game.end()
    if len(players) == 1:
        winner = game.player.keys()[0]
        اسمه = winner['name']
        محاولاته = winner['points']
        await e.reply(f"🎉 مبارك للاعب ( {اسمه=} ) - محاولاته المتبقية: {محاولاته}")
        game.end()
        return
    player_id, pdata = random.choice(list(players.items()))
    killer_name = pdata["name"]
    points = pdata["points"]
    if points <= 0:
        await e.reply(f"الله يرحمك ( {killer_name} ) — ماتت نقاطك")
        game.remove_player(player_id)
        return
    game.killer = player_id
    btns = [
        Button.inline("تحديد الضحية", data="choice_to_kill"),
        Button.inline("قتل عشوائي", data="autokill")
    ]
    await e.reply(f"أنت القاتل يا ( {killer_name} ) — اختر نوع القتل", buttons=btns)
    game.players[player_id]["points"] -= 1
@ABH.on(events.CallbackQuery(pattern=r"choice_to_kill|autokill|kill:(\d+)"))
async def kill_callback(e):
    chat = e.chat_id
    game = killamorder.get(chat)
    if not game:
        await e.delete()
        return
    killer = game.killer()
    if not killer or e.sender_id != killer:
        return
    data = e.data.decode()
    players = game.players()
    if data == "autokill":
        victim_id, victim_data = random.choice(list(players.items()))
        if victim_id == killer:
            game.del_killer()
            await e.edit(f"انتحر اللاعب ( {victim_data['name']} ) 🤦‍♂️")
            game.remove_player(victim_id)
            return
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
        await e.edit(txt, buttons=btns)
        return
    if data.startswith("kill:"):
        game.del_killer()
        victim_id = int(data.split(":")[1])
        victim = players[victim_id]["name"]
        game.remove_player(victim_id)
        await e.edit(f"تم قتل ( {victim} ) بنجاح")
        return
