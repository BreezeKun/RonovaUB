from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                            InlineQueryResultArticle, InputRichMessageContent)

from ..utilities import wiki_search


def build_rich_wiki_html(title, thumbnail, description, source_url, summary) -> str:

    return f"""
<img src="{thumbnail}"/>

<h1>{title}</h1>

<hr/>

<details>
<summary><b>📖 Summary</b></summary>
<blockquote>{summary}</blockquote>
</details>

<hr/>

<details open>
<summary><b>📝 Description</b></summary>
<blockquote>{description}<cite>Wikipedia</cite></blockquote>
</details>

<hr/>

<p>
🔗 <a href="{source_url}">Read full article</a>
</p>
"""

@Client.on_inline_query(filters.regex(r"wiki (.+)"))
async def inline_wiki(c: Client, q: InlineQuery):
    name      = q.matches[0].group(1)
    result    = await wiki_search(name)
    rich_text = build_rich_wiki_html(*result)

    await q.answer([
        InlineQueryResultArticle(
            title="send anime",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=rich_text)
            )
        )
    ], cache_time=0)