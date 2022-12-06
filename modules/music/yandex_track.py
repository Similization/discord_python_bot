import yandex_music

from modules.music.volume_info import VolumeInfo


class YandexTrack(VolumeInfo):
    def __init__(self, track: yandex_music.Track, catalog: str = "music/songs"):
        url = f"https://music.yandex.ru/track/{track.id}"
        super().__init__(
            volume=track,
            artists=track.artists,
            title=f"{self.volume.title} - {self.artists}",
            catalog=catalog,
            url=url,
        )
