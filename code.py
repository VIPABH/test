from ABH import ABH
import asyncio
async def x():
    await ABH.send_message(1910015590, ".")
    await asyncio.sleep(10)
async def s():
    while True:  
        await x()
if __name__ == "__main__":
    asyncio.run(s())
