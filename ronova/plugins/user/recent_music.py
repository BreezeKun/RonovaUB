
import curl_cffi

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import LAST_FM_API

API_KEY = LAST_FM_API
LASTFM_USER = "BreezeMeowMeow"


async def fetch_recent(m: Message):
    url = "https://ws.audioscrobbler.com/2.0/"

    params = {
        "method": "user.getRecentTracks",
        "user": LASTFM_USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": 1
    }

    try:
        # Fetch Last.fm data
        response = curl_cffi.get(
            url,
            params=params,
            impersonate="chrome",
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        # Print raw JSON response
        import json
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # Check API errors
        if "error" in data:
            await m.reply_text(
                f"Last.fm API Error: {data['message']}"
            )
            return

        tracks = data["recenttracks"]["track"]

        if not tracks:
            await m.reply_text("No recent tracks found.")
            return

        # Get latest track
        track = tracks[0]

        name = track["name"]
        artist = track["artist"]["#text"]
        album = track.get("album", {}).get("#text", "Unknown Album")

        # Get extralarge album artwork
        images = track.get("image", [])

        image = next(
            (
                img["#text"]
                for img in images
                if img["size"] == "extralarge" and img["#text"]
            ),
            None
        )

        # Check currently playing status
        now_playing = (
            track.get("@attr", {}).get("nowplaying") == "true"
        )

        status = (
            "🎧 <b>Currently Playing</b>"
            if now_playing
            else "🎵 <b>Recently Played</b>"
        )

        # Track URL
        track_url = track.get("url")

        # Caption
        caption = (
            f"{status}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🎵 <b>{name}</b>\n"
            f"🎤 {artist}\n"
            f"💿 {album}\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        # Listen button
        keyboard = None

        if track_url:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎧 Listen",
                        url=track_url
                    )
                ]
            ])

        # Send album artwork
        if image:
            await m.reply_photo(
                photo=image,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            await m.reply_text(
                caption,
                reply_markup=keyboard
            )

    except Exception as e:
        print("Last.fm ERROR:", repr(e))

        await m.reply_text(
            f"❌ Error fetching Last.fm data:\n{e}"
        )


@Client.on_message(filters.command("recent") & filters.me)
async def recent_music(c: Client, m: Message):
    await fetch_recent(m)
