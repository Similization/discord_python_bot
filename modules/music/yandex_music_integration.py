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

from modules.music.yandex_album import YandexAlbum
from modules.music.yandex_track import YandexTrack


class YAM:
    track_list: list[YandexTrack | YandexAlbum] = []
    project_path = ""

    def __init__(self):
        """Constructor"""
        self.client: Client

        with open("util/configuration.json", "r") as json_data_file:
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

    async def download_track(self, track_info: YandexTrack):
        full_path_to_track = f"{self.project_path}/{track_info.catalog}"
        if not os.path.exists(full_path_to_track):
            os.makedirs(full_path_to_track)

        # upload track
        track_info.volume.download(track_info.short_path)
        # add track to track list
        self.track_list.append(track_info)

    async def download_album(self, album_info: YandexAlbum):
        full_path_to_album = f"{self.project_path}/{album_info.short_path}"
        if not os.path.exists(full_path_to_album):
            os.makedirs(full_path_to_album)

        for volume in album_info.volume.volumes:
            for track in volume:
                track_cls = YandexTrack(track, catalog=album_info.short_path)
                track_cls.volume.download(track_cls.short_path)
                album_info.tracks.append(track_cls)

        self.track_list.append(album_info)

    async def find_by_type(
        self, name: str, _type: Literal["track", "album", "podcast episode", "podcast"]
    ) -> Optional[YandexTrack | YandexAlbum]:
        match _type:
            case "track":
                founded_tracks = self.client.search(name, type_="track").tracks
                if founded_tracks is not None:
                    return YandexTrack(track=founded_tracks.results[0])
            case "podcast episode":
                founded_podcast_episodes = self.client.search(
                    name, type_="podcast_episode"
                ).podcast_episodes
                if founded_podcast_episodes is not None:
                    return YandexTrack(
                        track=founded_podcast_episodes.results[0],
                        catalog="music/podcast_episodes",
                    )
            case "album":
                founded_albums = self.client.search(name).albums
                if founded_albums is not None:
                    return YandexAlbum(
                        album=founded_albums.results[0].with_tracks(),
                    )
            case "podcast":
                founded_podcasts = self.client.search(name, type_="podcast").podcasts
                if founded_podcasts is not None:
                    return YandexAlbum(
                        album=founded_podcasts.results[0],
                        catalog="music/podcasts",
                    )

    async def download(self, volume: YandexTrack | YandexAlbum):
        if volume in self.track_list:
            return
        if isinstance(volume, YandexTrack):
            await self.download_track(volume)
        elif isinstance(volume, YandexAlbum):
            await self.download_album(volume)
