import json

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import curl_cffi


async def fetch_recent(m: Message):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {"limit": 1}

    headers = {
        "Authorization": "Bearer BQAWRroRRedlPtsiwXdQ2c_fPq2Gl9z3EX7-ACelidyKexq59oAEI80JLHZ1NqGHyBa21Gtv6wc3tob2AMMwdCLN93CCyscyftwrxvdUekZUcdljfMvN_xtSfBX2sIGHTMPQUJpl05KBW5ERAEKgHBfjuzlIP6u8-DbKkmx8-HeED1USfUThuvATi8aWjEllKc3LK9w-Q3gFry3dk9HOoJFzINbygqD1mUYFDPsvGUE0KYRGO9mOP_uSPwMtW3ZBQBMrexXJBKCWoPhjXNm6VrPsSdV0J9ouUXdC1BQ0GUNYnL5IcF4whqWMX-36TftNZCqGeEvxDT1v9g",
        "Accept": "application/json"
    }

    response = curl_cffi.get(
        url,
        params=params,
        headers=headers,
        impersonate="chrome"
    )

    if response.status_code == 200:
        data = response.json()

        tracks = []

        for item in data.get("items", []):
            track = item["track"]
            album = track["album"]

            song_data = {
                "song": track["name"],
                "artists": [artist["name"] for artist in track["artists"]],
                "album": album["name"],
                "release_date": album.get("release_date"),
                "duration_ms": track["duration_ms"],
                "duration_minutes": round(track["duration_ms"] / 60000, 2),
                "played_at": item["played_at"],
                "album_cover": (
                    album["images"][0]["url"]
                    if album.get("images") else None
                ),
                "spotify_url": track["external_urls"]["spotify"],
                "track_id": track["id"],
                "track_uri": track["uri"],
                "popularity": track.get("popularity")
            }

            tracks.append(song_data)

        if not tracks:
            return await m.reply_text("🎧 No recently played songs found.")

        song_data = tracks[0]

        caption = (
            "🎧 <b>Recently Played</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🎵 <b>{song_data['song']}</b>\n"
            f"🎤 {', '.join(song_data['artists'])}\n"
            f"💿 {song_data['album']}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"⏱ <b>Duration:</b> {song_data['duration_minutes']} min\n"
            f"📅 <b>Released:</b> {song_data['release_date'] or 'Unknown'}\n"
            f"🔥 <b>Popularity:</b> {song_data['popularity']}/100\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<i>Enjoying your music? 🎶</i>"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎧 Listen on Spotify",
                    url=song_data["spotify_url"]
                )
            ]
        ])

        await m.reply_photo(
            photo=song_data["album_cover"],
            caption=caption,
            reply_markup=keyboard
        )

    else:
        await m.reply_text(
            f"❌ Spotify API Error: {response.status_code}"
        )


@Client.on_message(filters.command("recent") & filters.me)
async def recent_music(c: Client, m: Message):
    await fetch_recent(m)