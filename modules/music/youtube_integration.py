from typing import Optional

import youtube_dl

from modules.music.youtube_track import YouTubeTrack


class YTM:
    config: dict

    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def get_track(queue: str, config: dict) -> Optional[YouTubeTrack]:
        with youtube_dl.YoutubeDL(config["YDL_OPTIONS"]) as ydl:
            try:
                info = ydl.extract_info(queue, download=False)
                return YouTubeTrack(config=config, info=info)
            except youtube_dl.utils.DownloadError:
                return None
