from ABH import ABH as client
import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import SendReactionRequest, ReactionEmoji, ChatReactionsAll, ChatReactionsSome, ChatReactionsNone


async def hint(text):
    """دالة بسيطة لطباعة الأخطاء والتنبيهات"""
    print(f"[TIPS/ERROR]: {text}")

def print_all():
    print("--- [بدء عملية التفاعل والتوجيه] ---")


# 1. دالة التفاعل وفحص الإيموجيات المسموحة
async def react(event, chat=None, id=None, emojis=None):
    chat_id = chat if chat else event.chat_id
    msg_id = id if id else event.message.id
    
    try:
        print_all()
    except Exception:
        pass
        
    status = [0, 0]
    
    emoji = None
    try:
        # جلب الكيان بأمان
        try:
            peer = await ABH.get_input_entity(chat_id)
        except Exception:
            entity = await ABH.get_entity(chat_id)
            peer = await ABH.get_input_entity(entity)

        # معرفة وطباعة الإيموجيات المسموحة في القناة
        try:
            full_chat = await ABH(GetFullChannelRequest(peer))
            reactions = full_chat.full_chat.available_reactions
            
            if isinstance(reactions, ChatReactionsAll):
                print(f"التفاعلات المسموحة: جميع الإيموجيات القياسية (All)")
            elif isinstance(reactions, ChatReactionsSome):
                allowed_list = [r.emoticon for r in reactions.reactions if hasattr(r, 'emoticon')]
                print(f"الإيموجيات المسموحة المخصصة في القناة: {allowed_list}")
            elif isinstance(reactions, ChatReactionsNone):
                print(f"التفاعلات معطلة بالكامل في هذه القناة!")
        except Exception as r_err:
            print(f"لم يتم جلب تفاصيل التفاعلات: {r_err}")

        # زيادة المشاهدات
        try:
            await ABH(GetMessagesViewsRequest(
                peer=peer,
                id=[int(msg_id)],
                increment=True 
            ))
        except Exception:
            pass
            
        emoji = random.choice(emojis) if emojis else random.choice(['❤️', '🕊', '🌚'])
        
        # إرسال التفاعل مع معالجة الأخطاء
        try:
            await ABH(SendReactionRequest(
                peer=peer,
                msg_id=int(msg_id),
                reaction=[ReactionEmoji(emoticon=emoji)],
                big=False
            ))
            status[0] += 1
        except Exception as react_err:
            if "Invalid reaction provided" in str(react_err):
                await ABH(SendReactionRequest(
                    peer=peer,
                    msg_id=int(msg_id),
                    reaction=[ReactionEmoji(emoticon='❤️')],
                    big=False
                ))
                status[0] += 1
            else:
                raise react_err

        await asyncio.sleep(0.3)
        
    except Exception as e:
        status[1] += 1
        try:
            await hint(str(e))
        except Exception:
            print(f"Error in react loop: {e}")
            
    return status if status is not None else [0, 0]


# 2. دالة التوجيه الآمن (Try Forward)
async def try_forward(event, chat=None, id=None, to=None, drop_author=None):
    msg_id = id if id else getattr(event, 'id', None)
    raw_from = chat if chat else getattr(event, 'chat_id', None)
    raw_to = to if to else getattr(event, 'chat_id', None)

    try:
        if msg_id is not None:
            msg_id = int(msg_id)
        else:
            return False

        if isinstance(raw_from, str) and raw_from.isdigit():
            from_peer = int(raw_from)
        elif isinstance(raw_from, int):
            from_peer = raw_from
        else:
            from_peer = await client.get_input_entity(raw_from)

        if isinstance(raw_to, str) and raw_to.isdigit():
            target_chat = int(raw_to)
        elif isinstance(raw_to, int):
            target_chat = raw_to
        else:
            target_chat = await client.get_input_entity(raw_to)

        await client.forward_messages(
            entity=target_chat,
            messages=msg_id,
            from_peer=from_peer,
            drop_author=drop_author
        )
        return True

    except Exception as e:
        print(f"Forward Error: {e}")
        return False


# --- حدث تجريبي لتشغيل الدوال عند إرسال كلمة معينة ---
@client.on(events.NewMessage(pattern=r"تجربة"))
async def test_handler(event):
    await event.respond("جارٍ اختبار التفاعل والتوجيه...")
    
    # تجربة دالة التفاعل بإيموجي فراولة أو عشوائي
    status = await react(event, emojis=['🍓', '🔥', '❤️'])
    await event.respond(f"نتيجة التفاعلات الناجحة: {status[0]} | الفاشلة: {status[1]}")

