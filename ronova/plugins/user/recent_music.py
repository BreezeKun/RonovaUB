import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import curl_cffi


async def fetch_recent(m: Message):
    url = "https://www.last.fm/user/BreezeMeowMeow"

    response = curl_cffi.get(url, impersonate="chrome")
    response.raise_for_status()

    with open("website.html.txt", "w", encoding="utf-8") as file:
        file.write(response.text)

    with open("website.html.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    yt_url = re.findall(r'"([^"]*)"', lines[1758])[0]
    name = re.findall(r'"([^"]*)"', lines[1760])[0]
    artist = re.findall(r'"([^"]*)"', lines[1763])[0]
    image = re.findall(r'"([^"]*)"', lines[1806])[0]

    song_data = {
        "song": name,
        "artists": [artist],
        "album_cover": image,
        "spotify_url": yt_url
    }

    caption = (
        "🎧 <b>Currently Playing</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎵 <b>{song_data['song']}</b>\n"
        f"🎤 {', '.join(song_data['artists'])}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎧 Listen",
                url=song_data["spotify_url"]
            )
        ]
    ])

    if song_data["album_cover"]:
        await m.reply_photo(
            photo=song_data["album_cover"],
            caption=caption,
            reply_markup=keyboard
        )
    else:
        await m.reply_text(
            caption,
            reply_markup=keyboard
        )



@Client.on_message(filters.command("recent") & filters.me)
async def recent_music(c: Client, m: Message):
    await fetch_recent(m)