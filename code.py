from ABH import *
import inspect
def print_all():
  caller_frame = inspect.currentframe().f_back
  func_name = caller_frame.f_code.co_name
  caller_locals = caller_frame.f_locals
  items = list(caller_locals.items())[1:]
  formatted_items = []
  for k, v in items:
    if not isinstance(v, (str, int, float, bool, list, dict, set, tuple)):
      continue
    formatted_items.append(f"{k}={v}")
  result = " , ".join(formatted_items)
  print(f"متغيرات دالة ( {func_name} ): \n{result}")
@ABH.on(events.NewMessage)
async def _(e):
  x = 2
  y = 1
  s = '3e'
  k=20
  print_all()
