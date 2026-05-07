@client.on(events.NewMessage(incoming=True))
async def alias_resolver(event):
    if not event.text or not event.text[0] in ['/', '.', '!']:
        return

    parts = event.text.split(maxsplit=1)
    prefix = parts[0][0]
    trigger = parts[0][1:]
    args = parts[1] if len(parts) > 1 else ""

    real_command_name = r.hget("bot_aliases", trigger)

    if real_command_name:
        clean_name = real_command_name.lstrip('/.! ')
        new_text = f"{prefix}{clean_name} {args}".strip()
        
        # أهم خطوة: الحفاظ على الـ Reply الأصلي إذا وجد
        reply_msg = await event.get_reply_message()
        
        # تحديث نص الرسالة
        event.message.message = new_text
        event.message.text = new_text
        
        print(f"🔄 محاولة تشغيل: {new_text}")

        for handler, event_type in client.list_event_handlers():
            if isinstance(event_type, events.NewMessage):
                if event_type.filter(event):
                    try:
                        # نقوم بتمرير الـ reply_to_msg_id يدوياً لضمان عمل أوامر التقييد
                        if reply_msg:
                            event._reply_message = reply_msg
                            event.message.reply_to_msg_id = reply_msg.id
                        
                        await handler(event)
                        print(f"✅ نُفذ في الشات")
                        raise events.StopPropagation
                    except events.StopPropagation:
                        raise
                    except Exception as e:
                        print(f"❌ خطأ داخلي: {e}")
        
        raise events.StopPropagation
