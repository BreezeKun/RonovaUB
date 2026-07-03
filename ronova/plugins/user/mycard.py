import os
from PIL import Image

from enkacard2 import encbanner2
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, BOT


import os

async def get_card():
    os.makedirs("gi_downloads", exist_ok=True)

    async with encbanner2.ENC(uid="1817389136") as encard:
        result = await encard.creat()

    for char in result.card:
        name = (char.name or "").strip()
        if not name:
            name = str(char.id)

        safe_name = name

        img = char.card
        img = img.resize((800, int(img.height * (800 / img.width))), Image.LANCZOS)
        img.save(f"gi_downloads/{char.id}_{safe_name}.png", format="PNG", optimize=True)


@Client.on_message(filters.command("mycard", prefixes=PREFIXES))
async def mygicard(c:Client, m:Message):

    msg = await m.reply("please wait...")

    if not os.path.exists(f".enka_py"):
        await msg.edit("Downloading assests...")
        from enkanetwork import EnkaNetworkAPI
        enka_update = EnkaNetworkAPI()
        async with enka_update:
            await enka_update.update_assets()
    
    if not os.path.exists(f"gi_downloads"):
        await msg.edit("fetching data...")
        await get_card()

    results = await c.get_inline_bot_results(bot=BOT, query=f"genshin_card")

    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )
    await msg.delete()
    
    
