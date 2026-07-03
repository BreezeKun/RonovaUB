import os
from PIL import Image

from enkacard2 import encbanner2
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, BOT, g_id


async def get_card(uid: str = g_id):
    os.makedirs("gi_downloads", exist_ok=True)

    async with encbanner2.ENC(uid=uid) as encard:
        result = await encard.creat(2)

    for char in result.card:
        name = (char.name or "").strip() or str(char.id)
        safe_name = name.replace("/", "_")

        img = char.card
        img = img.resize(
            (800, int(img.height * (800 / img.width))),
            Image.LANCZOS
        )

        img.save(f"gi_downloads/{char.id}_{safe_name}.png", "PNG", optimize=True)

@Client.on_message(filters.command("mycard", prefixes=PREFIXES))
async def mygicard(c: Client, m: Message):

    msg = await m.reply("Generating your cards...")

    try:
        await get_card()

    except Exception as e:
        await msg.edit(f"Error:\n{e}")
        return

    try:
        results = await c.get_inline_bot_results(
            bot=BOT,
            query="genshin_card"
        )

        await c.send_inline_bot_result(
            chat_id=m.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_parameters=ReplyParameters(message_id=m.id)
        )

    except Exception as e:
        await msg.edit(f" Inline error:\n{e}")
        return

    await msg.delete()