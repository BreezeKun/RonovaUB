from ytmusicapi import YTMusic
import yt_dlp


class GetMusic:
    queue = []
    status = False

    def get_from_yt(self):
        if self.status:
            yt = YTMusic()

            results = yt.search(self.queue[0], filter="songs")

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

            self.queue.pop(0)

            return song

    def add_queue(self, music:str):
        if music not in self.queue:
            self.queue.append(music)

    def play_music(self):
        if not self.status:
            self.status = True
            return self.get_from_yt()

MUSIC_PLAYER = GetMusic()