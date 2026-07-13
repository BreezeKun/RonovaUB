from pyrogram import idle
import uvloop

from ronova import ub, bot
from .server import startServer

async def main():
    await bot.start()
    await ub.start()

    await startServer()

    print("Bot and UB started!")

    await idle()

    await bot.stop()
    await ub.stop()

uvloop.install()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())