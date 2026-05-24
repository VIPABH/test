from telethon import events, functions, types

# تخزين آخر custom reactions تم اكتشافها
CUSTOM_REACTIONS = set()

@ABH.on(events.Raw())
async def detect_custom_reactions(update):

    try:

        # تحديثات التفاعلات
        if isinstance(update, types.UpdateMessageReactions):

            reactions = update.reactions.results

            for r in reactions:

                # إذا كان التفاعل مميز Premium
                if isinstance(r.reaction, types.ReactionCustomEmoji):

                    doc_id = r.reaction.document_id

                    if doc_id not in CUSTOM_REACTIONS:

                        CUSTOM_REACTIONS.add(doc_id)

                        print(f"New Custom Reaction Found: {doc_id}")

        # عند وصول رسالة جديدة
        elif isinstance(update, types.UpdateNewMessage):

            message = update.message

            # إذا عدنا تفاعل مميز مخزن
            if CUSTOM_REACTIONS:

                reaction_id = next(iter(CUSTOM_REACTIONS))

                try:

                    await ABH(functions.messages.SendReactionRequest(
                        peer=message.peer_id,
                        msg_id=message.id,
                        reaction=[
                            types.ReactionCustomEmoji(
                                document_id=reaction_id
                            )
                        ],
                        big=True
                    ))

                    print(f"Applied reaction: {reaction_id}")

                except Exception as e:
                    print(f"Reaction failed: {e}")

    except Exception as e:
        print(f"Global Error: {e}")
