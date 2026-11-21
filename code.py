from ABH import *
from Resources import *
@ABH.on(events.NewMessage(pattern='^(عرض الاعدادات|الاعدادات|/settings)$')
async def settings(e):
    if not e.is_group:return
    a = await auth(e)
    if not a:return await e.reply('ماعندك رتبة ف ماتكدر تشوف الاعدادات')
    row_buttons = [
        Button.inline('اوامر الحماية', data='command_guard', style=blue, icon=5972226216353074147),
        Button.inline('اوامر المجموعة', data='command_group', style=blue, icon=6032609071373226027),
        Button.inline('اوامر ثانوية', data='command_mem', style=blue, icon=5305355874187880345),
        Button.inline('اوامر اخرى', data='command_other', style=blue, icon=5229113891081956317),
    ]
    buttons = chunk_list(row_buttons, 2)
    await PROFILE_SEND(e, 'تفضل الاقسام كدامك', buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=b'^command_'))
async def settings_callback(e):
    data = e.data.decode()
    arg = (data.split('_'))[1]
    translate = {'guard': 'اوامر الحماية', 'group': 'اوامر المجموعة', 'other': 'اوامر اخرى'}
    buttons = []
    translations = {
        "تحذير": "warn",
        "منع": "ban",
        "بوتات مضافة": "bot",
        "اوامر عام": "gcmd",
        "تعديل": "edit",
        "يوتيوب": "yt",
        "ايدي": "id",
        "همسة": "whs",
        "العاب": "game",
        "رفع": "up",
        "ردود": "rpl",
        "تنظيف": "cln",
        "ميم": "meme",
        "توب": "top",
        "اختصارات": "shc",
        "ترقية": "prm",
        "ترقية وصلاحياتها": "prmp",
        "اوامر مقيدة": "rcmd",
        }
    if arg == 'guard':
        args = ["تحذير", "منع", "بوتات مضافة", "اوامر عام", "تعديل"]
    elif arg == 'group':
        args = ["ايدي", "همسة", "العاب", "رفع"]
    elif arg == 'other':
        args = ["اختصارات", "ترقية", "ترقية وصلاحياتها", "اوامر مقيدة"]
    elif arg == 'mem':
        args = ["يوتيوب", "رفع", "ردود", "تنظيف", "ميم", "توب"]
    for name in args:
        l = lock(e, name)
        buttons.append([
            Button.inline(name, data=f'command_{arg}:{translations[name]}', style=blue, icon=5258096772776991776),
            Button.inline(name, data=f'toggle:{name}', style=green if l else red, icon=on if l else off), 
            ]
            )
    await e.edit(f'تفضل عزيزي هذا قسم ( {translate[arg]} )', buttons=buttons)
