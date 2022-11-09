import asyncio
from typing import Optional

import disnake

from modules.music.yandex_music_integration import TrackInfo, AlbumInfo


class MusicQueue:
    def __init__(
        self,
        inter: disnake.ApplicationCommandInteraction,
        voice_client: Optional[disnake.VoiceClient],
    ):
        self.inter = inter
        self.track_position: int = 0
        self.is_repeatable: bool = False
        self.voice_client: disnake.VoiceClient = voice_client
        self.track_list: list[TrackInfo] = list()
        self.track_count: int = len(self.track_list)
        self.current_track = None

    async def play(self):
        while len(self.track_list) != 0:
            self.current_track = self.track_list[self.track_position]
            self.voice_client.play(
                disnake.FFmpegPCMAudio(f"{self.current_track.short_path}")
            )

            while self.voice_client.is_playing() or self.voice_client.is_paused():
                await asyncio.sleep(1)

            self.voice_client.stop()

            if not self.is_repeatable:
                self.track_list.remove(self.current_track)
                self.track_count = len(self.track_list)

            if self.track_count != 0:
                self.track_position = (self.track_position + 1) % self.track_count

    async def add_volume(self, volume: TrackInfo | AlbumInfo):
        if isinstance(volume, TrackInfo):
            self.track_list.append(volume)
        elif isinstance(volume, AlbumInfo):
            for track in volume.tracks:
                self.track_list.append(track)
        self.track_count = len(self.track_list)

    async def is_playing(self):
        return self.voice_client.is_playing()

    async def pause(self):
        self.voice_client.pause()

    async def resume(self):
        self.voice_client.resume()

    async def skip(self, to: int = 1, delete: bool = False):
        for _ in range(to):
            self.voice_client.stop()
            if delete:
                self.track_list.remove(self.current_track)

    async def clear(self):
        self.track_list.clear()

    async def stop(self):
        await self.voice_client.disconnect(force=True)

    async def repeat(self):
        self.is_repeatable = True

    async def get_url(self):
        track_id = self.current_track.track.id
        url = f"https://music.yandex.ru/track/{track_id}"
        return url
