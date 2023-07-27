from __future__ import annotations
import pygame 
import cv2 
import subprocess
import os 
import time 
from typing import Tuple 
from .post_processing import PostProcessing
from . import get_ffmpeg_path


class ParallelVideo:
    def __init__(self, path: str, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, sound=None) -> None:
        
        self.path = path
        self.name, self.ext = os.path.splitext(os.path.basename(self.path))

        self._vid = cv2.VideoCapture(self.path)

        self.frame_count = self._vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_rate = self._vid.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1 / self.frame_rate
        self.duration = self.frame_count / self.frame_rate
        self.original_size = (int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.current_size = self.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

        self.frame_data = None
        self.frame_surf = None
        
        self.subs = subs
        self.post_func = post_process
        self.interp = interp

        if sound is None:
            self._sound = pygame.mixer.Sound(subprocess.run(f'"{get_ffmpeg_path()}" -i "{self.path}" -ar 44100 -f wav -loglevel quiet -', capture_output=True).stdout)
        else:
            self._sound = sound
        self._channel = None

        self.active = False 
        self._starting_time = 0

        self.play()

    def __str__(self) -> str:
        return f"<Video(path={self.path})>"
    
    def _update(self) -> bool:
        n = False

        t = self.get_pos()

        if t <= self.duration:

            while t > self._vid.get(cv2.CAP_PROP_POS_FRAMES) * self.frame_delay:
                has_frame, data = self._vid.read()
                
                if has_frame:
                    if self.original_size != self.current_size:
                        data = cv2.resize(data, dsize=self.current_size, interpolation=self.interp)
                    data = self.post_func(data)

                    self.frame_data = data
                    self.frame_surf = pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")

                    if self.subs is not None:
                        self._write_subs()

                    n = True
                else:
                    break

        else:
            self.stop()
    
        return n

    def _write_subs(self) -> None:
        p = self.get_pos()
        
        if p >= self.subs.start:
            if p > self.subs.end:
                self.subs._get_next()
                self._write_subs()
            else:
                self.frame_surf.blit(self.subs.surf, (self.current_size[0] / 2 - self.subs.surf.get_width() / 2, self.current_size[1] - self.subs.surf.get_height() - 50))

    def copy_sound(self, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR) -> ParallelVideo:
        return ParallelVideo(self.path, subs, post_process, interp, self._sound)

    def draw(self, surf: pygame.Surface, pos: Tuple[int, int], force_draw=True) -> bool:
        if self._update() or force_draw:
            if self.frame_surf is not None:
                surf.blit(self.frame_surf, pos)
                return True
        return False

    def resize(self, size: Tuple[int, int]) -> None:
        self.current_size = size

    def change_resolution(self, height: int) -> None:
        self.current_size = (int(height * self.aspect_ratio), height)
        
    def close(self) -> None:
        self.stop()
        self._vid.release()

    def get_pos(self) -> float:
        return time.time() - self._starting_time if self.active else 0
    
    def set_volume(self, vol: float) -> None:
        if self.active:
            self._channel.set_volume(vol)

    def get_volume(self) -> float:
        return self._channel.get_volume() if self.active else 1.0

    def play(self) -> None:
        self.active = True
        self._vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self._channel = pygame.mixer.find_channel()
        self._channel.play(self._sound)
        self._starting_time = time.time()

    def restart(self) -> None:
        self.stop() 
        self.play()

    def stop(self) -> None:
        self.active = False
        self.frame_data = None
        self.frame_surf = None

        if self._channel is not None:
            self._channel.stop()
            self._channel = None