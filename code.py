from ABH import ABH
x = {}
@ABH.on(events.NewMessage)
async def x(e):
  for i in range(50, 502):
    msg = await ABH.get_messages("x04ou", ids=i)
    if not msg or not msg.file:
        continue
    title = msg.file.title
    if tiltle not in x:
      url = msg.file.url
      x[title] = link
    text = e.text
    if text in x:
      await ABH.send_file(e.chat_id, x[title])
    elif text == "دز":
      await e.reply(str(x))
