from telethon import events, functions, types
from ABH import *
LAST_REACTION = None

# يكتشف التفاعلات الجديدة
@ABH.on(events.Raw())
async def watch_reactions(update):

    global LAST_REACTION

    try:

        # إذا صار تحديث تفاعل
        if isinstance(update, types.UpdateMessageReactions):

            if not update.reactions:
                return

            for r in update.reactions.results:

                # فقط التفاعل المميز
                if isinstance(r.reaction, types.ReactionCustomEmoji):

                    LAST_REACTION = r.reaction.document_id

                    print(f"Detected Custom Reaction: {LAST_REACTION}")

    except Exception as e:
        print(e)


# تطبيق آخر reaction مكتشف
@ABH.on(events.NewMessage(pattern="فاعل"))
async def react(event):

    global LAST_REACTION

    if not LAST_REACTION:
        return await event.reply("ماكو تفاعل مميز مكتشف لحد الآن")

    try:

        await ABH(functions.messages.SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.id,
            reaction=[
                types.ReactionCustomEmoji(
                    document_id=LAST_REACTION
                )
            ],
            big=True
        ))

        await event.reply("تم التفاعل")

    except Exception as e:

        await event.reply(str(e))
