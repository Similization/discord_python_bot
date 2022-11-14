import asyncio
from typing import Optional

import disnake

from modules.music.yandex_music_integration import TrackInfo, AlbumInfo


class MusicQueueError(Exception):
    pass


class MusicQueue:
    def __init__(
        self,
        inter: Optional[disnake.ApplicationCommandInteraction],
        voice_client: Optional[disnake.VoiceClient],
    ):
        self.inter = inter
        self.delete: bool = False
        self.track_position: int = 0
        self.is_repeatable: bool = False
        self.voice_client: disnake.VoiceClient = voice_client
        self.track_list: list[TrackInfo] = list()
        self.current_track = None

    async def play(self):
        while len(self.track_list) != 0:
            self.current_track = self.track_list[self.track_position]

            if self.voice_client is None:
                raise MusicQueueError("Voice client is None")

            try:
                await self.send_message(f"now is playing: {self.current_track.title}")
            except MusicQueueError as e:
                print(e)

            if not self.voice_client.is_playing():
                self.voice_client.play(
                    disnake.FFmpegPCMAudio(f"{self.current_track.short_path}")
                )

            while self.voice_client is not None:
                if self.voice_client.is_playing() or self.voice_client.is_paused():
                    await asyncio.sleep(1)
                else:
                    break
            await self.next()

    async def add_volume(self, volume: TrackInfo | AlbumInfo):
        if isinstance(volume, TrackInfo):
            self.track_list.append(volume)
        elif isinstance(volume, AlbumInfo):
            for track in volume.tracks:
                self.track_list.append(track)

    async def is_playing(self):
        return self.voice_client.is_playing()

    async def pause(self) -> bool:
        if self.voice_client.is_playing():
            self.voice_client.pause()
        return self.voice_client.is_paused()

    async def resume(self) -> bool:
        if self.voice_client.is_paused():
            self.voice_client.resume()
        return self.voice_client.is_playing()

    async def next(self):
        if self.voice_client.is_playing():
            self.voice_client.stop()
        if not self.is_repeatable or self.is_repeatable and self.delete:
            current_track = self.track_list[self.track_position]
            self.track_list.remove(current_track)
        elif len(self.track_list) != 0:
            self.track_position = (self.track_position + 1) % len(self.track_list)

    async def skip(self, to: int = 1) -> int:
        skipped_count: int = 1
        while skipped_count < to and len(self.track_list) != 0:
            await self.next()
            skipped_count += 1
        return skipped_count

    async def clear(self):
        self.track_list.clear()

    async def stop(self):
        await self.voice_client.disconnect(force=True)
        self.voice_client = None

    async def repeat(self, delete_track_on_skip: bool = False) -> bool:
        if self.is_repeatable:
            return False
        self.is_repeatable = True
        self.delete = delete_track_on_skip
        return True

    async def no_repeat(self):
        if not self.is_repeatable:
            return False
        self.is_repeatable = False
        self.delete = True
        return True

    async def get_url(self):
        track_id = self.current_track.track.id
        url = f"https://music.yandex.ru/track/{track_id}"
        return url

    async def send_message(self, message: str):
        if self.inter is None:
            raise MusicQueueError("Application command interaction not set")
        else:
            await self.inter.channel.send(message)

    async def get_list(self):
        return self.track_list
