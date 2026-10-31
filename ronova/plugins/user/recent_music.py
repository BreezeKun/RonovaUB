import json

from pyrogram import Client, filters
from pyrogram.types import Message
import curl_cffi

async def fetch_recent(m:Message):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {"limit": 1}

    headers = {
        "Authorization": "Bearer BQBa5V34JyOlrT0gkw9k5bIia8g7a0htFrXqXWWGUWeVpCL5bpRe9YRqJdlaz-GuCEcz_h0y0ShusB89aGOcAuOKKHMFqEFH9q59hOgaW_b4WL_a5XjEcjam7snDkaCw1SS7cjfOEH6eOeDacRFGxW2LRZY0y4Tpjs6jZrC5K7BQqe76WWRwX1S_dpCJ1m-6oUNKsdpJqkGI01s5PVJoKhoNBAtwng0yOnx9XMdxCXx6rWP8eLmzmOu9NDOYG03L6kX3ZMKQZ6w16FlpgkwBEuSb0k3wdRzsMXPDUOLv4qY-oA689hW_XE2cso0tvalmqE5pyKuFYjTdVg",
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

            await m.reply_photo(
                photo=song_data["album_cover"],
                caption=f"🎵 SONG:{song_data["song"]}\n🎤 ARTIST: {", ".join(song_data["artists"])}\n💿 ALBUM: {song_data["album"]}\n⏱️ DURATION: {song_data["duration_minutes"]} minutes"
            )
@Client.on_message(filters.command("recent")&filters.me)
async def recent_music(c:Client, m:Message):
    await fetch_recent(m)