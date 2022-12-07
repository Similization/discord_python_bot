from typing import Any


class VolumeInfo:
    def __init__(
        self,
        volume,
        artists: list[Any],
        title: str,
        catalog: str = "",
        extension: str = "mp3",
        url: str = "",
    ):
        self.volume = volume
        if len(artists) != 0:
            self.artists = self.get_artists_names(artists=artists)
            self.title = f"{title} - {self.artists}"
        else:
            self.artists = []
            self.title = f"{title}"
        self.catalog = catalog
        self.extension = extension
        self.short_path = f"{self.catalog}/{self.title}.{self.extension}"
        self.url = url

    @staticmethod
    def get_artists_names(artists):
        return ", ".join([artist.name for artist in artists])

    def get_url(self) -> str:
        return self.url
