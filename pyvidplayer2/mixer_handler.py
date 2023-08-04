import pygame
from io import BytesIO


class MixerHandler:
    def __init__(self) -> None:
        pass

    def get_busy(self):
        return pygame.mixer.music.get_busy()

    def load(self, bytes):
        pygame.mixer.music.load(BytesIO(bytes))

    def unload(self):
        pygame.mixer.music.unload()

    def play(self):
        pygame.mixer.music.play()

    def set_volume(self, vol):
        pygame.mixer.music.set_volume(min(1.0, max(0.0, vol)))
        
    def get_volume(self):
        return pygame.mixer.music.get_volume()

    def get_pos(self):
        return max(0, pygame.mixer.music.get_pos()) / 1000

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        # unpausing the mixer when nothing has been loaded causes weird behaviour 
        if pygame.mixer.music.get_pos() != -1:
            pygame.mixer.music.unpause()