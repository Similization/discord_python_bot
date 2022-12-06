import json
import random
from typing import Optional, Literal, Union

import disnake
import yandex_music
from yandex_music import StationResult, Client

from modules.music.music_queue import MusicQueue
from modules.music.yandex_track import YandexTrack
from modules.music.yandex_music_integration import YAM
from modules.music.yandex_station import YandexStation


class YandexRadioError(Exception):
    pass


class YandexRadio:
    def __init__(
        self,
        client: yandex_music.Client = YAM().client,
        text_channel: Optional[disnake.TextChannel] = None,
        inter: Optional[disnake.ApplicationCommandInteraction] = None,
        station: Optional[YandexStation] = None,
        voice_client: Optional[disnake.VoiceClient] = None,
    ) -> None:
        self.client: yandex_music.Client = client
        self.voice_channel = text_channel
        self.inter = inter
        self.current_station: Optional[YandexStation] = station
        self.music_queue = MusicQueue(inter=inter, voice_client=voice_client)
        self.available_stations: list[StationResult] = client.rotor_stations_list()
        self.station_names = [radio.station.name for radio in self.available_stations]
        self.radio_started: bool = False

    def set_station(self, station_name: str):
        result = None
        for station_result in self.available_stations:
            if station_result.station.name != station_name:
                continue
            result = station_result
            break

        if result is None:
            raise YandexRadioError("station name is not correct, please check it again")

        self.current_station = YandexStation(client=self.client, station_result=result)

    def set_random_station(self):
        available_stations = self.client.rotor_stations_list()
        random_station = random.choice(available_stations)
        self.current_station = YandexStation(
            client=self.client, station_result=random_station
        )

    def change_station_setting(
        self,
        mood_energy: Literal["fun", "active", "calm", "sad", "all"] = "all",
        diversity: Literal["favorite", "popular", "discover", "default"] = "default",
        language: Literal["not-russian", "russian", "any"] = "any",
        type_: Literal["rotor", "generative"] = "rotor",
        timeout: Union[int, float] = None,
    ) -> bool:
        if self.current_station is None:
            raise YandexRadioError("current station is None")
        return self.current_station.change_settings(
            mood_energy=mood_energy,
            diversity=diversity,
            language=language,
            type_=type_,
            timeout=timeout,
        )

    def get_current_station_info(self):
        if self.current_station is None:
            raise YandexRadioError("current station is None")
        return self.current_station.get_info()

    def set_send_information_about_song(
        self, information_is_sending: bool = False
    ) -> bool:
        if information_is_sending:
            self.music_queue.inter = None
        return self.music_queue.inter is not None

    def start_radio(self):
        if not self.radio_started:
            self.current_station.start_radio()
            self.__update_songs()
            self.music_queue.play()

            while True:
                if len(self.music_queue.track_list) > 2:
                    continue
                self.__update_songs()
        else:
            raise YandexRadioError("radio is already started!")

    def __update_songs(self):
        track = self.current_station.get_current_track()
        volume = YandexTrack(track=track, catalog="radio")
        self.music_queue.add_volume(volume=volume)
        self.current_station.play_next()


if __name__ == "__main__":
    with open("../../util/configuration.json", "r") as json_data_file:
        data = json.load(json_data_file)
    yandex_token = data["yandex"]["token"]
    _client = Client(token=yandex_token)
    _radio = YandexRadio(client=_client)
    _radio.set_random_station()
    print(_radio.get_current_station_info())
