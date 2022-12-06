from typing import Literal, Union, Optional

from yandex_music import (
    StationResult,
    StationTracksResult,
    Station,
    Client,
    Track,
    exceptions,
)


class YandexStationError(Exception):
    pass


class YandexStation:
    def __init__(
        self,
        client: Client,
        station_result: StationResult,
    ) -> None:
        self.client: Client = client
        self.station_result: StationResult = station_result
        station: Station = self.station_result.station
        self.station_id: str = f"{station.id.type}:{station.id.tag}"
        self.station_from: str = station.id_for_from
        self.station_tracks_result: Optional[StationTracksResult] = None
        self.station_tracks: list[Track] = list()
        self.current_track: Optional[Track] = None

    def start_radio(self):
        self.__update_batch_of_tracks(None)
        self.__update_current_track()

    def change_settings(
        self,
        mood_energy: Literal["fun", "active", "calm", "sad", "all"] = "all",
        diversity: Literal["favorite", "popular", "discover", "default"] = "default",
        language: Literal["not-russian", "russian", "any"] = "any",
        type_: Literal["rotor", "generative"] = "rotor",
        timeout: Union[int, float] = None,
    ) -> bool:
        result: bool = False
        try:
            result = self.client.rotor_station_settings2(
                station=self.station_id,
                mood_energy=mood_energy,
                diversity=diversity,
                language=language,
                type_=type_,
                timeout=timeout,
            )
        except exceptions.YandexMusicError as e:
            print(e)
        return result

    def play_next(self):
        self.__send_track_ended(
            track=self.current_track, batch_id=self.station_tracks_result.batch_id
        )
        self.station_tracks.remove(self.current_track)

        if len(self.station_tracks) == 0:
            self.__update_batch_of_tracks(self.current_track.track_id)

        self.__update_current_track()

    def get_current_track(self) -> Track:
        return self.current_track

    def get_info(self):
        available_keys = ["language", "diversity", "mood_energy"]
        setting_dict = self.station_result.settings2.__dict__
        setting_keys = list(setting_dict.keys())

        for key in setting_keys:
            if key in available_keys:
                continue
            setting_dict.pop(key)

        station_id = self.station_result.station.id
        setting_dict["type"] = station_id.type
        setting_dict["tag"] = station_id.tag
        return setting_dict

    def __update_batch_of_tracks(self, queue=None):
        self.station_tracks_result = self.client.rotor_station_tracks(
            station=self.station_id, settings2=True, queue=queue
        )
        if self.station_tracks_result is None:
            raise YandexStationError("StationTracksResult is None")
        self.station_tracks = [
            tracks_result.track for tracks_result in self.station_tracks_result.sequence
        ]
        self.__send_radio_started(batch_id=self.station_tracks_result.batch_id)

    def __send_radio_started(self, batch_id):
        self.client.rotor_station_feedback_radio_started(
            station=self.station_id, from_=self.station_from, batch_id=batch_id
        )

    def __update_current_track(self):
        self.current_track = self.station_tracks[0]
        self.__send_track_started(
            track_id=self.current_track.id, batch_id=self.station_tracks_result.batch_id
        )

    def __send_track_started(self, track_id, batch_id):
        self.client.rotor_station_feedback_track_started(
            station=self.station_id, track_id=track_id, batch_id=batch_id
        )

    def __send_track_ended(self, track, batch_id):
        self.client.rotor_station_feedback_track_finished(
            station=self.station_id,
            track_id=track.id,
            total_played_seconds=0,
            batch_id=batch_id,
        )
