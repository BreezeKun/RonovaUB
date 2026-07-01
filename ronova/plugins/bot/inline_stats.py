import sys

from pyrogram import Client, filters, __version__
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputRichMessageContent,
    InputRichMessage
)

from ..utilities import eval_helper
from config import ADMIN_ID

@Client.on_inline_query(filters.regex("latency") & filters.user(ADMIN_ID))
async def inline_ping(c: Client, q: InlineQuery):

    latency = eval_helper.get('latency', 0)

    rich_text = f"""
<h2>📊 Bot Dashboard</h2>

<table>
<tr>
<th align="left">Metric</th>
<th align="right">Value</th>
</tr>

<tr>
<td>Latency</td>
<td><code>{latency} ms</code></td>
</tr>




<tr>
<td>Python</td>
<td><code>{sys.version.split()[0]}</code></td>
</tr>




<aside>
Bot is running smoothly with optimized performance.
<cite>Runtime Monitor</cite>
</aside>

<hr/>

<p><i>Inline Stats Panel • Live Data</i></p>
"""

    await q.answer([
        InlineQueryResultArticle(
            title="📊 Open Dashboard",
            input_message_content=InputRichMessageContent(
                InputRichMessage(rich_text)
            )
        )
    ], cache_time=0)
