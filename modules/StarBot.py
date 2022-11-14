import platform
from typing import Optional

import disnake
from disnake.ext import commands
from disnake.ext.commands import Bot

from modules.music.MusicQueue import MusicQueue


def load_opus():
    current_platform = platform.system()

    if current_platform == "Linux":
        disnake.opus.load_opus("libopus.so")
    elif current_platform == "Darwin":
        disnake.opus.load_opus("util/lib-opus.dylib")
    elif current_platform == "Windows":
        disnake.opus.load_opus("util/lib-opus-0_x86.dll")
        disnake.opus.load_opus("util/lib-opus-0_x64.dll")


class StarBot(Bot):
    def __init__(
        self,
        config: dict,
        intents: disnake.Intents = None,
        music_queue: Optional[MusicQueue] = None,
    ):
        load_opus()

        if intents is None:
            intents = disnake.Intents.default()
            intents.members = True
            intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=intents
        )

        self.config = config
        self.music_queue: Optional[MusicQueue] = music_queue

    def run(self):
        super().run(self.config["token"])
