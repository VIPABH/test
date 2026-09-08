from Resources import *
from ABH import *
@ABH.on(events.NewMessage(pattern=r"^(تقييد عام|مخفي قيد[هة])(?:\s+(@\w+|\d{6,10}|\d{1,5}))?(?:\s+(\d{6,10}|\d{2,5}))?$"))
async def restrict_user(event):
    if not event.is_group:return
    reply = None
    chat_id = event.chat_id
    user, id, t = extractfree(event.text)
    if user:
        fulluser = await ABH.get_entity(user)
        if not fulluser:
            await chs(event, "عذرا هذا المستخدم غير موجود.")
            return
        target = fulluser.id
    elif id:
        target = id
    else:
        reply = await event.get_reply_message()
        if reply:
            target = reply.sender_id
        else:
            await chs(event, "يجب تحديد المستخدم أو الرد على رسالته.")
            return            
    x = await auth(event, x=False, to=event.sender_id)
    a = await auth(event, x=False, to=target)
    if not x: return await event.reply('😂')
    if target == wfffp: 
        await chs(event, "😂")
        return
    can = authers(x, a)
    if not can:
        await chs(event, f"عذرا بس ماتكدر تقيد {a}")
        return
    await event.delete()
    end_time_str = r.hget(str(chat_id), str(target))
    if end_time_str:
        now = int(time.time())
        remaining = int(end_time_str) - now
        if remaining > 0:
            minutes, seconds = divmod(remaining, 60)
            remaining_str = f"( {minutes:02}:{seconds:02} )"
            await chs(event, f"المستخدم مقيد مسبقا باقي على تقييده {remaining_str}")
            return
    t = int(t) if t else 20
    if x in res_time:
        if t < 10:
            t = 10
        else:
            max_allowed_time = res_time[x]
            t = min(t, max_allowed_time)
    name = await ment(target)
    try:
        p = await ABH(GetParticipantRequest(
            channel=int(chat_id),
            participant=int(target)
        ))
        is_member = True
    except UserNotParticipantError:
        is_member = False
        p = None
    except Exception as e:
        await hint('gurd 73*' + str(e))
        return
    if is_member:
        if isinstance(p.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
            await res(f"{chat_id}:{target}", True, t*60)
            await chs(event, f'تم كتم {name} مدة {t} دقيقة')
            await send(
                event,
                f'#تقييد_عام\n'
                f'تم كتم {a if a else "المستخدم"} \n'
                f'اسمه ( {name} ) \n'
                f'🆔 ايديه: ( `{target}` )\n'
                f'👤 بواسطة {x} \n'
                f'اسمه: ( {await mention(event)} ) \n'
                f'ايديه: ( `{event.sender_id}` )\n'
                f'المده ( {t} د ) \n'
                f'الرابط {await link(event)}'
            )
            return
    await res(f"{chat_id}:{target}", not is_member, int(t) * 60)
    c = f"تم تقييد {name} لمدة {t} دقيقة."
    if not is_member: 
        c += '\n ماكدرت اقيد المستخدم لانه مغادر 🚪'
    await ABH.send_file(event.chat_id, "media/res.MP4", caption=c)
    await send(
        event,
        f'#تقييد_عام\n'
        f'تم تقييد المستخدم \n'
        f'اسمه ( {name} ) \n'
        f'🆔 ايديه: ( `{target}` )\n'
        f'👤 بواسطة {x} \n'
        f'اسمه: ( {await mention(event)} ) \n'
        f'ايديه: ( `{event.sender_id}` )\n'
        f'المده ( {t} د ) \n'
        f'الرابط {await link(event)}'
    )
    if reply:
        await try_forward(reply)
        try:
            await reply.delete()
        except:
            pass
    signres(chat_id, 'تقييد عام', event.sender_id, target)
