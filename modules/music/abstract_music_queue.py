from abc import ABC, abstractmethod


class AbstractMusicQueue(ABC):
    @abstractmethod
    async def play(self):
        pass

    @abstractmethod
    async def add_volume(self, volume):
        pass

    @abstractmethod
    async def add_volumes(self, volumes):
        pass

    @abstractmethod
    async def is_playing(self):
        pass

    @abstractmethod
    async def pause(self):
        pass

    @abstractmethod
    async def resume(self):
        pass

    @abstractmethod
    async def next(self):
        pass

    @abstractmethod
    async def skip(self, to: int = 1):
        pass

    @abstractmethod
    async def clear(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def repeat(self):
        pass

    @abstractmethod
    async def no_repeat(self):
        pass

    @abstractmethod
    async def get_track(self):
        pass

    @abstractmethod
    async def get_list(self):
        pass
