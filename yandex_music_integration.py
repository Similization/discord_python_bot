import json
import os
from time import sleep
from typing import Union

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager

import yandex_music.exceptions
from yandex_music import Client


class YAM:
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
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome(desired_capabilities=capabilities,
                                  executable_path=ChromeDriverManager().install())
        driver.get("https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")

        token = None

        while token is None and self.__private_is_active(driver):
            sleep(1)
            try:
                logs_raw = driver.get_log("performance")
                for lr in logs_raw:
                    log = json.loads(lr["message"])["message"]
                    url_fragment = log.get('params', {}).get('frame', {}).get('urlFragment')

                    if url_fragment:
                        token = url_fragment.split('&')[0].split('=')[1]
            except Exception as e:
                print(e)

        try:
            driver.close()
        except Exception as e:
            print(e)

        return token

    @staticmethod
    def __private_get_album_artists_names(artists: list) -> str:
        artists_names = []
        for artist in artists:
            artists_names.append(artist.name)
        return ' ,'.join(artists_names)

    async def download_song_by_name(self, song_name: str) -> str:
        track = self.client.search(song_name, type_='track').tracks.results[0]
        artists_names = self.__private_get_album_artists_names(track.artists)
        track.download(f"music/songs/{track.title} - {artists_names}.mp3")
        return f"{track.title} - {artists_names}"

    async def download_album_by_name(self, album_name: str) -> str:
        album = self.client.search(album_name).albums.results[0].with_tracks()
        artists_names = self.__private_get_album_artists_names(album.artists)

        path_to_album = f"{os.path.dirname(__file__)}/music/albums/{album.title} - {artists_names}"
        if not os.path.exists(path_to_album):
            os.mkdir(path_to_album)

        tracks_in_album = []
        for volume in album.volumes:
            for track in volume:
                track_artists_names = self.__private_get_album_artists_names(track.artists)
                track.download(f"{path_to_album}/{track.title} - {track_artists_names}.mp3")
                tracks_in_album.append(track)
        return f"{album.title} - {artists_names}"
