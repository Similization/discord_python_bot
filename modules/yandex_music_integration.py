import json
import os
from time import sleep
from typing import Union, Literal, Optional

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager

import yandex_music.exceptions
from yandex_music import Client


def get_artists_names(artists: list) -> str:
    artists_names = []
    for artist in artists:
        artists_names.append(artist.name)
    return ", ".join(artists_names)


class TrackInfo:
    def __init__(self, value: yandex_music.Track = None, catalog: str = "music/songs"):
        self.track = value
        self.artists = get_artists_names(self.track.artists)
        self.title = f"{self.track.title} - {self.artists}"
        self.catalog = catalog
        self.extension = "mp3"
        self.short_path = (
            f"{self.catalog}/{self.track.title} - {self.artists}.{self.extension}"
        )


class AlbumInfo:
    def __init__(
            self,
            value: yandex_music.Album = None,
            tracks: list[TrackInfo] = None,
            catalog: str = "music/albums",
    ):
        self.album = value
        self.artists = get_artists_names(self.album.artists)
        self.title = f"{self.album.title} - {self.artists}"
        self.catalog = catalog
        self.short_path = f"{self.catalog}/{self.album.title} - {self.artists}"
        self.tracks = list() if tracks is None else tracks


class YAM:
    track_list: list[TrackInfo | AlbumInfo] = []

    def __init__(self):
        """Constructor"""
        self.client: Client

        with open("configuration.json", "r") as json_data_file:
            data = json.load(json_data_file)
        yandex_token = data["yandex"]["token"]

        try:
            if yandex_token is None:
                raise TypeError
            self.client = Client(yandex_token).init()
        except Union[yandex_music.exceptions.UnauthorizedError, TypeError]:
            # if token has expired - we get new one
            yandex_token = self.__private_get_token()

            data["yandex"]["token"] = yandex_token
            with open("configuration.json", "w") as json_data_file:
                json.dump(data, json_data_file)
            self.client = Client(yandex_token).init()

    @staticmethod
    def __private_is_active(driver) -> bool:
        try:
            driver.execute(Command.GET_ALL_COOKIES)
            return True
        except Exception as e:
            print(e)
            return False

    def __private_get_token(self):
        # make chrome log requests
        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"performance": "ALL"}
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        driver = webdriver.Chrome(
            desired_capabilities=capabilities,
            executable_path=ChromeDriverManager().install(),
        )
        driver.get(
            "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d"
        )

        token = None

        while token is None and self.__private_is_active(driver):
            sleep(1)
            try:
                logs_raw = driver.get_log("performance")
                for lr in logs_raw:
                    log = json.loads(lr["message"])["message"]
                    url_fragment = (
                        log.get("params", {}).get("frame", {}).get("urlFragment")
                    )

                    if url_fragment:
                        token = url_fragment.split("&")[0].split("=")[1]
            except Exception as e:
                print(e)

        try:
            driver.close()
        except Exception as e:
            print(e)

        return token

    @staticmethod
    def __private_get_artists_names(artists) -> str:
        artists_names = []
        for artist in artists:
            artists_names.append(artist.name)
        return ", ".join(artists_names)

    async def download_track(self, track_info: TrackInfo):
        full_path_to_track = (
            f"{os.path.split(os.path.dirname(__file__))[0]}/{track_info.catalog}"
        )
        if not os.path.exists(full_path_to_track):
            os.makedirs(full_path_to_track)

        # upload track
        track_info.track.download(track_info.short_path)
        # add track to track list
        self.track_list.append(track_info)

    async def download_album(self, album_info: AlbumInfo):
        full_path_to_album = (
            f"{os.path.split(os.path.dirname(__file__))[0]}/{album_info.short_path}"
        )
        if not os.path.exists(full_path_to_album):
            os.makedirs(full_path_to_album)

        for volume in album_info.album.volumes:
            for track in volume:
                track_cls = TrackInfo(track, catalog=album_info.short_path)
                track_cls.track.download(track_cls.short_path)
                album_info.tracks.append(track_cls)

        self.track_list.append(album_info)

    async def find_by_type(
            self,
            name: str,
            _type: Literal["track", "album", "podcast episode", "podcast"]
    ) -> Optional[TrackInfo | AlbumInfo]:
        match _type:
            case "track":
                founded_tracks = self.client.search(name, type_="track").tracks
                if founded_tracks is not None:
                    return TrackInfo(value=founded_tracks.results[0])
            case "podcast episode":
                founded_podcast_episodes = self.client.search(
                    name, type_="podcast_episode"
                ).podcast_episodes
                if founded_podcast_episodes is not None:
                    return TrackInfo(
                        value=founded_podcast_episodes.results[0],
                        catalog="music/podcast_episodes",
                    )
            case "album":
                founded_albums = self.client.search(name).albums
                if founded_albums is not None:
                    return AlbumInfo(
                        value=founded_albums.results[0].with_tracks(),
                    )
            case "podcast":
                founded_podcasts = self.client.search(name, type_="podcast").podcasts
                if founded_podcasts is not None:
                    return AlbumInfo(
                        value=founded_podcasts.results[0],
                        catalog="music/podcasts",
                    )

    async def download(self, volume: TrackInfo | AlbumInfo):
        if isinstance(volume, TrackInfo):
            await self.download_track(volume)
        elif isinstance(volume, AlbumInfo):
            await self.download_album(volume)
