from typing import Any

from modules.music.volume_info import VolumeInfo


class YouTubeTrack(VolumeInfo):
    def __init__(self, config: dict, info: Any):
        # queue can be the name of the song or url to it
        # need to get artist name from it somehow
        # for now it is unknown
        self.config = config
        self.info = info
        super().__init__(
            volume=None,
            artists=[],
            title=self.info["title"],
            url=self.info["webpage_url"],
        )
