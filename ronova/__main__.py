import asyncio
import pytz
from datetime import datetime

from pyrogram import idle

from ronova import ub, bot
from .server import startServer
import uvloop



async def close_session():
    from .plugins.utilities import session
    if session and not session.closed:
        await session.close()

def close_db():
    from .plugins.database import db
    if db and db.conn:
        db.close()

async def startup():

    zn = pytz.timezone("Asia/Kolkata")
    time = datetime.now(zn)

    await bot.start()
    await ub.start()

    from .plugins.utilities import VOICE_PLAYER

    await VOICE_PLAYER.start()

    await bot.send_message(
        -1003792991167,
        f"bot has been started - {time}"
    )

    from .plugins.database import sudo_methods
    sudo_methods.build_cache()

    asyncio.create_task(startServer())

    print("Bot and UB started!")

    await idle()
    

async def on_stop():
    try:
        if bot.is_connected:
            await bot.send_message(
                -1003792991167,
                "Bot has been stopped"
            )
    except Exception as e:
        print(f"Could not send stop message: {e}")

    try:
        if ub.is_connected:
            await ub.stop()
    except Exception as e:
        print(f"Could not stop UB: {e}")

    try:
        if bot.is_connected:
            await bot.stop()
    except Exception as e:
        print(f"Could not stop bot: {e}")

    try:
        await close_session()
    except Exception as e:
        print(f"Could not close session: {e}")


uvloop.install()
async def main():
    try:
        await startup()
        
    finally:
        await on_stop()


if __name__ == "__main__":
    asyncio.run(main())
