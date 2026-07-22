from pyrogram import idle
from ronova import ub, bot
from .server import startServer
import asyncio
import uvloop

async def close_session():
    from .plugins.utilities import session
    if session and not session.closed:
        await session.close()


uvloop.install()
async def main():
    try:
        await bot.start()
        await ub.start()

        asyncio.create_task(startServer())

        print("Bot and UB started!")

        await idle()

    finally:
        try:
            if ub.is_connected:
                await ub.stop()
        except Exception:
            pass

        try:
            if bot.is_connected:
                await bot.stop()
        except Exception:
            pass

        try:
            await close_session()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())