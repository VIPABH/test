from ABH import *
import inspect
def print_all():
  caller_frame = inspect.currentframe().f_back
  func_name = caller_frame.f_code.co_name
  caller_locals = caller_frame.f_locals
  result = " , ".join(f"{k}={v}" for k, v in caller_locals.items())
  print(f"متغيرات دالة ( {func_name} ): \n{result}")
@ABH.on(events.NewMessage)
async def _(e):
  x = 2
  y = 1
  s = '3e'
  k=20
  print_all()
