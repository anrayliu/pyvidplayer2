import cv2
import pygame
from .post_processing import PostProcessing
from typing import Tuple


class Webcam:
    def __init__(self, device: int, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR) -> None:
        
        self.device = device

        self._vid = cv2.VideoCapture(self.device)

        if not self._vid.isOpened():
            raise FileNotFoundError(f'Could not open device {self.device}')

        self.original_size = (int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.current_size = self.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

        self.frame_data = None
        self.frame_surf = None
        
        self.active = False
        self.paused = False

        self.post_func = post_process
        self.interp = interp

        self.play()

    def _update(self) -> bool:
        n = False

        if self.active and not self.paused:
            has_frame, data = self._vid.read()
            
            if has_frame:
                if self.original_size != self.current_size:
                    data = cv2.resize(data, dsize=self.current_size, interpolation=self.interp)
                data = self.post_func(data)

                self.frame_data = data
                self.frame_surf = self._create_frame(data)

                n = True

        return n
    
    def play(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False
        self.frame_data = None
        self.frame_surf = None
        self.paused = False 

    def resize(self, size: Tuple[int, int]) -> None:
        self.current_size = size

    def change_resolution(self, height: int) -> None:
        self.current_size = (int(height * self.aspect_ratio), height)

    def close(self) -> None:
        self.stop()
        self._vid.release()

    def get_paused(self) -> bool:
        # here because the original pyvidplayer had get_paused
        return self.paused
    
    def toggle_pause(self) -> None:
        self.resume() if self.paused else self.pause()

    def pause(self) -> None:
        if self.active:
            self.paused = True

    def resume(self) -> None:
        if self.active:
            self.paused = False

    def get_pos(self) -> float:
        pass

    def draw(self, surf, pos: Tuple[int, int], force_draw=True) -> bool:
        if self._update() or force_draw:
            if self.frame_surf is not None:
                self._render_frame(surf, pos)
                return True
        return False

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf, pos):
        surf.blit(self.frame_surf, pos)
    
    def preview(self):
        pass

