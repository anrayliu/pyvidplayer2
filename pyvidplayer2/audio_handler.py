from abc import ABC, abstractmethod


class AudioHandler(ABC):
    '''
    Interface for audio handlers, used internally to communicate with audio backends
    '''

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_busy(self) -> bool:
        '''
        Currently playing. Pausing does not affect busyness.
        '''

    @abstractmethod
    def get_num_channels(self) -> int:
        '''
        Returns output device channels if available. Returns 0 otherwise.
        '''

    @abstractmethod
    def close(self) -> None:
        '''
        Releases audio backend resources.
        '''

    @abstractmethod
    def unload(self) -> None:
        '''
        Releases loaded audio chunk.
        '''

    @abstractmethod
    def load(self, audio_chunk: bytes) -> None:
        '''
        Load an audio chunk into backend.
        '''

    @abstractmethod
    def get_loaded(self) -> bool:
        '''
        Returns whether an audio chunk is loaded.
        '''

    @abstractmethod
    def set_volume(self, vol: float) -> None:
        '''
        Sets the volume between 0.0 (min) and 1.0 (max).
        '''

    @abstractmethod
    def get_volume(self) -> float:
        '''
        Returns volume number.
        '''

    @abstractmethod
    def get_pos(self) -> float:
        '''
        Returns how many total seconds of audio have been played, across all loaded chunks.
        '''

    @abstractmethod
    def play(self) -> None:
        '''
        Starts playing audio.
        '''

    @abstractmethod
    def stop(self) -> None:
        '''
        Stops playing audio.
        '''

    @abstractmethod
    def pause(self) -> None:
        '''
        Pauses audio playback. Does not affect start/stop busyness.
        '''

    @abstractmethod
    def unpause(self) -> None:
        '''
        Unpauses audio playback. Does not affect start/stop busyness.
        '''

    @abstractmethod
    def get_paused(self) -> bool:
        '''
        Returns pause status.
        '''

    @abstractmethod
    def mute(self) -> None:
        '''
        Mutes audio. Does not affect volume.
        '''

    @abstractmethod
    def unmute(self) -> None:
        '''
        Unmutes audio. Does not affect volume.
        '''

    @abstractmethod
    def get_muted(self) -> bool:
        '''
        Returns muted status of audio.
        '''
