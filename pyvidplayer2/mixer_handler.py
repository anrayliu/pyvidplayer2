from io import BytesIO

import pygame

from .audio_handler import AudioHandler


class MixerHandler(AudioHandler):
    def __init__(self):
        self.muted = False
        self.loaded = False
        self.volume = 1

        pygame.mixer.music.unload()

    def get_busy(self):
        return pygame.mixer.music.get_busy()

    def load(self, bytes_):
        pygame.mixer.music.load(BytesIO(bytes_), "wav")
        self.loaded = True

    def get_num_channels(self):
        try:
            return pygame.mixer.get_init()[2]
        except IndexError:
            return 0

    def unload(self):
        self.stop()
        pygame.mixer.music.unload()
        self.loaded = False

    def play(self):
        pygame.mixer.music.play()

    def set_volume(self, vol):
        self.volume = vol
        pygame.mixer.music.set_volume(min(1.0, max(0.0, vol)))

    def get_volume(self):
        return self.volume

    def get_pos(self):
        # pygame does not reset audio position when audio is unloaded
        if not pygame.mixer.music.get_busy() and pygame.mixer.music.get_pos() != 0:
            return 0
        return max(0, pygame.mixer.music.get_pos()) / 1000.0

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        # unpausing the mixer when nothing has been loaded causes weird behaviour 
        if pygame.mixer.music.get_pos() != -1:
            pygame.mixer.music.unpause()

    def mute(self):
        self.muted = True
        pygame.mixer.music.set_volume(0)

    def unmute(self):
        self.muted = False
        self.set_volume(self.volume)

    # does not uninit mixer because other videos may still need it
    def close(self):
        if self.loaded:
            self.unload()

    # not ideal, should've used properties instead
    # still better to be consistent with old patterns until refactors can be made
    def get_muted(self):
        return self.muted
    
    def get_loaded(self):
        return self.loaded
    
    def get_paused(self):
        return self.paused
