import json
import os
from time import sleep
from typing import Union, Literal

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
    return ' ,'.join(artists_names)


class TrackInfo:
    def __init__(self, value: yandex_music.Track = None, catalog: str = "music/songs"):
        self.track = value
        self.artists = get_artists_names(self.track.artists)
        self.title = f"{self.track.title} - {self.artists}"
        self.catalog = catalog
        self.extension = "mp3"
        self.short_path = f"{self.catalog}/{self.track.title} - {self.artists}.{self.extension}"


PodcastEpisodeInfo = TrackInfo


class AlbumInfo:
    def __init__(self, value: yandex_music.Album = None, tracks: list = None, catalog: str = "music/albums"):
        self.album = value
        self.artists = get_artists_names(self.album.artists)
        self.title = f"{self.album.title} - {self.artists}"
        self.catalog = catalog
        self.short_path = f"{self.catalog}/{self.album.title} - {self.artists}"
        self.tracks = tracks


PodcastAlbumInfo = AlbumInfo


class YAM:
    track_list: list = []

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
    def __private_get_artists_names(artists) -> str:
        artists_names = []
        for artist in artists:
            artists_names.append(artist.name)
        return ' ,'.join(artists_names)

    async def download(self, name: str, _type: Literal["track", "album", "podcast episode", "podcast"]):
        match _type:
            case "track": pass



    async def download_song_by_name(self, song_name: str) -> str:
        track = TrackInfo(value=self.client.search(song_name, type_='track').tracks.results[0])
        # upload track
        track.track.download(track.short_path)
        # add track to track list
        self.track_list.append(track)
        return track.title

    async def download_album_by_name(self, album_name: str) -> str:
        album = AlbumInfo(value=self.client.search(album_name).albums.results[0].with_tracks())

        full_path_to_album = f"{os.path.dirname(__file__)}/{album.short_path}"
        if not os.path.exists(full_path_to_album):
            os.mkdir(full_path_to_album)

        tracks_in_album = []
        for volume in album.album.volumes:
            for track in volume:
                track_cls = TrackInfo(track, catalog=album.short_path)
                track.download(track_cls.short_path)
                tracks_in_album.append(track_cls)

        return album.title

    async def download_podcast_by_name(self, podcast_name: str) -> str:
        var = self.client.search(podcast_name, type_='podcast')
        podcast = PodcastAlbumInfo(value=self.client.search(podcast_name, type_='podcast')
                                   .podcast_episodes
                                   .results[0], catalog="music/podcasts")

        full_path_to_podcast = f"{os.path.dirname(__file__)}/{podcast.short_path}"
        if not os.path.exists(full_path_to_podcast):
            os.mkdir(full_path_to_podcast)

        tracks_in_album = []
        for volume in podcast.album.volumes:
            for track in volume:
                track_cls = TrackInfo(track, catalog=podcast.short_path)
                track.download(track_cls.short_path)
                tracks_in_album.append(track_cls)

        return podcast.title

    async def download_podcast_by_episode(self, podcast_episode: str) -> str:
        podcast = PodcastEpisodeInfo(value=self.client.search(podcast_episode, type_='podcast_episode')
                                     .podcast_episodes
                                     .results[0], catalog="music/podcast_episodes")
        # upload podcast
        podcast.track.download(podcast.short_path)
        # add track to track list
        self.track_list.append(podcast)
        return podcast.title
