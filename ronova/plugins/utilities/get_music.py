# music.py

from pathlib import Path
from ytmusicapi import YTMusic
import yt_dlp


DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


class GetMusic:
    def __init__(self):
        self.queue = []

    def add_queue(self, music: str):
        self.queue.append(music)

    def has_queue(self):
        return bool(self.queue)

    def get_next(self):
        if not self.queue:
            return None

        query = self.queue.pop(0)

        yt = YTMusic()
        results = yt.search(query, filter="songs")

        if not results:
            return None

        song = results[0]

        url = f"https://www.youtube.com/watch?v={song['videoId']}"

        ydl_opts = {
            "format": "ba[abr<=80]/ba",
            "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

        return {
            "title": info.get("title"),
            "artist": ", ".join(
                artist["name"]
                for artist in song.get("artists", [])
            ),
            "video_id": song.get("videoId"),
            "youtube_url": url,
            "duration": info.get("duration"),
            "duration_string": self.format_duration(
                info.get("duration")
            ),
            "extension": info.get("ext"),
            "format_id": info.get("format_id"),
            "bitrate": info.get("abr"),
            "filesize": info.get("filesize"),
            "filesize_approx": info.get("filesize_approx"),
            "filename": filename,
        }

    @staticmethod
    def format_duration(seconds):
        if seconds is None:
            return None

        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02}:{seconds:02}"

        return f"{minutes}:{seconds:02}"


MUSIC_PLAYER = GetMusic()