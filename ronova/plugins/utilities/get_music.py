from ytmusicapi import YTMusic
import yt_dlp


class GetMusic:
    queue = []

    def get_from_yt(self, music:str):
        yt = YTMusic()

        results = yt.search(music, filter="songs")

        if not results:
            return print("No data found")

        song = results[0]

        url = f"https://www.youtube.com/watch?v={song['videoId']}"

        ydl_opts = {
            "format": "ba[abr<=80]/ba",
            "outtmpl": "%(title)s.%(ext)s",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])