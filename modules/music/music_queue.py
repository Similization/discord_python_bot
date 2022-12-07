import asyncio
from typing import Optional

import disnake

from modules.music.abstract_music_queue import AbstractMusicQueue
from modules.music.yandex_track import YandexTrack
from modules.music.yandex_album import YandexAlbum
from modules.music.youtube_track import YouTubeTrack


class MusicQueueError(Exception):
    pass


class MusicQueue(AbstractMusicQueue):
    def __init__(
        self,
        inter: Optional[disnake.ApplicationCommandInteraction],
        voice_client: Optional[disnake.VoiceClient],
    ):
        self.inter = inter
        self.delete: bool = False
        self.skip_full: bool = False
        self.is_repeatable: bool = False
        self.voice_client: disnake.VoiceClient = voice_client
        self.track_position: int = 0
        self.volume_position: int = 0
        self.current_track: Optional[YandexTrack | YouTubeTrack] = None
        self.current_volume: Optional[YandexTrack | YouTubeTrack | YandexAlbum] = None
        self.volume_list: list[YandexTrack | YouTubeTrack | YandexAlbum] = []

    async def play(self):
        while len(self.volume_list) != 0:
            if self.voice_client is None:
                raise MusicQueueError("Voice client is None")

            self.current_volume = self.volume_list[self.volume_position]

            try:
                await self.send_message(f"Now is playing: {self.current_volume.title}")
            except MusicQueueError as e:
                print(e)

            if not self.voice_client.is_playing():
                await self.__play_volume(volume=self.current_volume)

            while self.voice_client is not None:
                if self.voice_client.is_playing() or self.voice_client.is_paused():
                    await asyncio.sleep(1)
                else:
                    break
            await self.next()
        await self.stop()

    async def __play_volume(self, volume: YandexTrack | YandexAlbum | YouTubeTrack):
        if isinstance(volume, YandexAlbum):
            await self.__play_album(album=volume)
        else:
            await self.__play_track(track=volume)

    async def __play_track(self, track: YandexTrack | YouTubeTrack):
        self.current_track = track
        if isinstance(track, YouTubeTrack):
            url = track.info["formats"][0]["url"]
            options = track.config["FFMPEG_OPTIONS"]

            self.voice_client.play(
                disnake.FFmpegPCMAudio(executable="util/ffmpeg", source=url, **options)
            )
        else:
            self.voice_client.play(disnake.FFmpegPCMAudio(f"{track.short_path}"))

    async def __play_album(self, album: YandexAlbum):
        for track in album.tracks:
            await self.__play_track(track=track)

    async def add_volume(self, volume: YandexTrack | YandexAlbum | YouTubeTrack):
        self.volume_list.append(volume)

    async def add_volumes(
        self, volumes: list[YandexTrack | YandexAlbum | YouTubeTrack]
    ):
        self.volume_list.extend(volumes)

    async def is_playing(self) -> bool:
        if self.voice_client is None:
            raise MusicQueueError("Voice client is None")
        return self.voice_client.is_playing()

    async def pause(self) -> bool:
        if self.voice_client.is_playing():
            self.voice_client.pause()
        return self.voice_client.is_paused()

    async def resume(self) -> bool:
        if self.voice_client.is_paused():
            self.voice_client.resume()
        return self.voice_client.is_playing()

    async def next_track(self):
        if not self.is_repeatable or self.is_repeatable and self.delete:
            current_track = self.current_volume.tracks[self.track_position]
            self.current_volume.tracks.remove(current_track)
        elif len(self.current_volume.tracks) != 0:
            self.track_position = (self.track_position + 1) % len(
                self.current_volume.tracks
            )
        else:
            self.track_position = 0
            await self.next_volume()

    async def next_volume(self):
        if not self.is_repeatable or self.is_repeatable and self.delete:
            current_volume = self.volume_list[self.volume_position]
            self.volume_list.remove(current_volume)

        elif len(self.volume_list) != 0:
            self.volume_position = (self.volume_position + 1) % len(self.volume_list)

    async def next(self):
        if (
            isinstance(self.current_volume, YouTubeTrack | YandexTrack)
            or self.skip_full
        ):
            await self.next_volume()
        else:
            await self.next_volume()

    async def skip(self, to: int = 1, skip_full: bool = False) -> int:
        self.skip_full = skip_full
        skipped_count: int = 0
        if self.voice_client.is_playing():
            self.voice_client.stop()
            skipped_count += 1
        while skipped_count < to and len(self.volume_list) != 0:
            await self.next()
            skipped_count += 1
        return skipped_count

    async def clear(self):
        self.volume_list.clear()

    async def stop(self):
        await self.clear()
        await self.voice_client.disconnect(force=True)
        self.voice_client = None

    async def repeat(self, delete_track_on_skip: bool = False) -> str:
        if not self.is_repeatable:
            self.is_repeatable = True
            result = "Music was set on repeat. "
        else:
            result = "Music was on repeat already. "
        if self.delete != delete_track_on_skip:
            self.delete = delete_track_on_skip
            result += (
                f"Option delete on skip was {'' if delete_track_on_skip else 'un'}set"
            )
        if result != "":
            return result
        return "Nothing changed"

    async def no_repeat(self) -> str:
        if not self.is_repeatable:
            return "Music wasn't on repeat already"
        self.is_repeatable = False
        self.delete = True
        return "Music has been taken off repeat"

    async def get_url(self) -> str:
        return self.current_volume.get_url()

    async def send_message(self, message: str):
        if self.inter is None:
            raise MusicQueueError("Application command interaction not set")
        else:
            await self.inter.channel.send(message)

    async def get_track(self) -> Optional[YandexTrack | YouTubeTrack]:
        return self.current_track

    async def get_volume(self) -> Optional[YandexTrack | YandexAlbum | YouTubeTrack]:
        return self.current_volume

    async def get_list(self) -> list[YandexTrack | YandexAlbum | YouTubeTrack]:
        return self.volume_list
