import asyncio
import uuid

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ChosenInlineResult
)

from config import ADMIN_ID, sudo
from ..premium.emoji_allies import emojis

CACHE = {}


async def change_text(text: str):
    words = text.split()
    result = []

    for word in words:
        key = word.lower()
        if key in emojis:
            result.append(emojis[key])
        else:
            result.append(word)

    return " ".join(result)


@Client.on_inline_query(filters.regex("prem (.+)"))
async def emo_in(c: Client, q: InlineQuery):

    allowed_users = ADMIN_ID + sudo

    if q.from_user.id not in allowed_users:
        return

    raw_text = q.matches[0].group(1)
    styled = await change_text(raw_text)

    key = str(uuid.uuid4())
    CACHE[key] = styled

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ Processing...", callback_data="noop")]
    ])

    await q.answer([
        InlineQueryResultArticle(
            id=key,
            title="Premium Text",
            input_message_content=InputTextMessageContent(
                message_text="please wait..."
            ),
            reply_markup=keyboard
        )
    ], cache_time=0)


@Client.on_chosen_inline_result()
async def on_chosen(c: Client, r: ChosenInlineResult):

    if not r.inline_message_id:
        print("No inline_message_id")
        return

    await asyncio.sleep(0.5)

    text = CACHE.get(r.result_id)

    if not text:
        print("Cache miss")
        return

    try:
        await c.edit_inline_text(
            inline_message_id=r.inline_message_id,
            text=text,
            reply_markup=None
        )
        del CACHE[r.result_id]

    except Exception as e:
        print("Edit error", e)