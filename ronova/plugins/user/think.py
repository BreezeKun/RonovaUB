from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import ADMIN_ID, PREFIXES, BOT
from ..utilities import eval_helper, AiSearch


@Client.on_message(filters.command("think", prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def think(c: Client, m: Message):
    args = m.command[1:]

    if not args:
        return await m.reply(
            "<b>Usage:</b>\n"
            "<code>think &lt;question&gt;</code>\n"
            "<code>think adv &lt;question&gt;</code>",
            parse_mode="html"
        )

    is_adv = args[0].lower() == "adv"
    query = " ".join(args[1:] if is_adv else args)

    await m.reply("wait...")

    ai = AiSearch(query)

    if is_adv:
        results = await ai.search()
        context, result = ai.build_context(results)
        answer = await ai.fetch_answer(context, result)
        print(result)
    else:
        answer = await ai.fetch_answer()

    html = answer or "<p>No response</p>"

    key = f"{m.chat.id}_{m.id}"

    eval_helper[key] = html

    results = await c.get_inline_bot_results(
        bot=BOT,
        query=f"think {key}"
    )

    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )