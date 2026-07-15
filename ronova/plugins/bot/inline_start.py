from pyrogram import Client, filters
from pyrogram.types import (Message, ReplyParameters, InputRichMessage, 
                            InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery,
                            InlineQueryResultArticle, InputRichMessageContent)
from pyrogram.enums import ButtonStyle

from ronova import get_uptime
from ..filters import starts


def rich_text_setup():
    up = get_uptime()

    return f"""
    <img src="https://i.ibb.co/RTzpvx9Z/x.jpg"/>

    <h1>RonovaUB</h1>
    <p>A powerful <b>Telegram Userbot</b></p>

    <hr/>

    <details><summary>Stats</summary>
    <table bordered striped>
    <caption>Bot Status</caption>
    <tr>
    <th>Metric</th>
    <th>Value</th>
    </tr>
    <tr>
    <td>Uptime</td>
    <td><code>{up}</code></td>
    </tr>
    </table>
    </details>

    <hr/>

    <details><summary>Available Commands</summary>
    <table bordered striped>
    <caption>Command Reference</caption>
    <tr>
    <th>Command</th>
    <th>Description</th>
    <th>Usage</th>
    </tr>
    <tr>
    <td><code>.eval</code></td>
    <td>Execute Python code and get the result</td>
    <td><code>.eval 1 + 1</code></td>
    </tr>
    <tr>
    <td><code>.bash</code></td>
    <td>Run a shell/terminal command</td>
    <td><code>.bash ls -la</code></td>
    </tr>
    <tr>
    <td><code>.ping</code></td>
    <td>Get server latency</td>
    <td><code>.ping</code></td>
    </tr>
    <tr>
    <td><code>.del</code></td>
    <td>Delete a replied-to message</td>
    <td>Reply + <code>.del</code></td>
    </tr>
    </table>
    <p>Visit the source repo for the complete list of commands and features.</p>
    </details>

    <hr/>

    <blockquote><cite>
    <p>💬 <b>Contact:</b> This bot also works as a contact medium between the user and the owner. Instead of DMing directly, you can send a message to the bot admin through the bot.</p></cite>
    </blockquote>

    <hr/>

    <footer>Use the button below to visit the source repo.</footer>
"""


@Client.on_message(filters.command("start"))
async def start_message(c: Client, m: Message):
    chat_id = m.chat.id
    rich_text = rich_text_setup()

    await c.send_reaction(chat_id, message_id=m.id, emoji="🔥", big=True)

    await c.send_rich_message(
        chat_id=chat_id,
        rich_message=InputRichMessage(rich_text),
        reply_parameters=ReplyParameters(message_id=m.id),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Repo", url="https://github.com/BreezeKun/RonovaUB", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_inline_query(filters.regex("start"))
async def start_inline(c: Client, q: InlineQuery):
    rich_text = rich_text_setup()

    await q.answer([
        InlineQueryResultArticle(
            title="start rich",
            input_message_content=InputRichMessageContent(
                InputRichMessage(rich_text)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Repo", url="https://github.com/BreezeKun/RonovaUB", style=ButtonStyle.PRIMARY)]
            ])
        )
    ], cache_time=0)


@Client.on_guest_message(starts(prefix="start"))
async def start_guest(c: Client, m: Message):
    rich_text = rich_text_setup()
    query_id = m.guest_query_id

    if m.reply_to_message:
        return

    await c.answer_guest_query(
        guest_query_id=query_id,
        result=InlineQueryResultArticle(
            title="start rich",
            input_message_content=InputRichMessageContent(
                InputRichMessage(rich_text)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Repo", url="https://github.com/BreezeKun/RonovaUB", style=ButtonStyle.PRIMARY)]
            ])
        )
    )
