import yandex_music

from modules.music.yandex_track import YandexTrack
from modules.music.volume_info import VolumeInfo


class YandexAlbum(VolumeInfo):
    def __init__(
        self,
        album: yandex_music.Album,
        catalog: str = "music/albums",
        tracks: list[YandexTrack] = list,
    ):
        url = f"https://music.yandex.ru/album/{album.id}"
        super().__init__(
            volume=album,
            artists=album.artists,
            title=f"{self.volume.title} - {self.artists}",
            catalog=catalog,
            url=url,
        )
        self.tracks = tracks
