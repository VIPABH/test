import asyncio
from ABH import ABH  # تأكد أن هذا الملف (ABH.py) موجود بنفس المجلد

async def x():
    await ABH.send_message(1910015590, ".")
    print("تم إرسال الرسالة ✅")
    await asyncio.sleep(10)

async def main():
    while True:
        await x()

if __name__ == "__main__":
    asyncio.run(main())
