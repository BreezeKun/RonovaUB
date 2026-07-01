from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                             InlineQueryResultArticle, InputRichMessageContent)

from ..utilities import word_search


def _escape(text: str) -> str:
    """Minimal HTML escaping for user/API-sourced text."""
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def build_rich_html(result: dict) -> str:
    if not result or result.get("error"):
        return (
            "<h2>Word not found</h2>"
            "<p>No dictionary entry could be located for that query.</p>"
        )

    word = _escape(result.get("word") or "")
    phonetic = _escape(result.get("phonetic") or "")
    origin = _escape(result.get("origin") or "")
    audio = result.get("audio")
    meanings = result.get("meanings") or []
    sources = result.get("source") or []

    parts = []

    # Header block
    parts.append(f"<h1>{word}</h1>")
    if phonetic:
        parts.append(f"<p><code>{phonetic}</code></p>")
    if audio:
        parts.append(
            f'<figure><audio src="{_escape(audio)}"></audio>'
            f"<figcaption>Pronunciation</figcaption></figure>"
        )

    if origin:
        parts.append(f"<blockquote>{origin}</blockquote>")

    if phonetic or audio or origin:
        parts.append("<hr/>")

    # Meanings
    for i, m in enumerate(meanings):
        pos = _escape(m.get("part_of_speech") or "")
        parts.append(f"<h3>{pos}</h3>")

        defs = m.get("definitions") or []
        if defs:
            parts.append("<ol>")
            for d in defs:
                definition = _escape(d.get("definition") or "")
                example = d.get("example")
                parts.append(f"<li>{definition}")
                if example:
                    parts.append(f"<br><em>\u201c{_escape(example)}\u201d</em>")
                parts.append("</li>")
            parts.append("</ol>")

        synonyms = m.get("synonyms") or []
        antonyms = m.get("antonyms") or []

        if synonyms or antonyms:
            parts.append("<table bordered>")
            if synonyms:
                parts.append(
                    f"<tr><th align=\"left\">Synonyms</th>"
                    f"<td>{', '.join(_escape(s) for s in synonyms)}</td></tr>"
                )
            if antonyms:
                parts.append(
                    f"<tr><th align=\"left\">Antonyms</th>"
                    f"<td>{', '.join(_escape(a) for a in antonyms)}</td></tr>"
                )
            parts.append("</table>")

        if i < len(meanings) - 1:
            parts.append("<hr/>")

    if sources:
        parts.append("<hr/>")
        link = _escape(sources[0])
        parts.append(f'<footer>Source: <a href="{link}">{link}</a></footer>')

    return "".join(parts)


@Client.on_inline_query(filters.regex(r"word (.+)"))
async def inline_ani(c: Client, q: InlineQuery):
    name = q.matches[0].group(1)
    result = await word_search(name)
    rich_text = build_rich_html(result)

    await q.answer([
        InlineQueryResultArticle(
            title=f"Define: {name}",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=rich_text)
            )
        )
    ], cache_time=0)