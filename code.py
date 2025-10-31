import asyncio
from ABH import ABH

async def x():
    await ABH.send_message(1910015590, ".")
    await asyncio.sleep(10)

async def main():
    while True:
        await x()

if __name__ == "__main__":
    ABH.loop.run_until_complete(main())
