import cv2
import pygame
import time
import numpy as np 
from typing import Callable, Union, Tuple
from .post_processing import PostProcessing
from .error import Pyvidplayer2Error


class Webcam:
    '''
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    '''

    def __init__(self, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none, interp: Union[str, int] = "linear", fps: int = 30, cam_id: int = 0) -> None:
        self._vid = cv2.VideoCapture(cam_id)

        if not self._vid.isOpened():
            raise Pyvidplayer2Error("Failed to find a webcam.")

        self.original_size = (int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.current_size = self.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

        self.frame_data = None
        self.frame_surf = None
        
        self.active = False

        self.post_func = post_process
        self.interp = interp
        self.fps = fps
        self.cam_id = cam_id

        self._frames = 0
        self._last_tick = 0

        self.set_interp(self.interp)

        self.play()

    def __str__(self) -> str:
        return f"<Webcam(fps={self.fps})>"

    def _update(self):
        if self.active:

            if time.time() - self._last_tick > 1 / self.fps:

                has_frame, data = self._vid.read()
                
                if has_frame:
                    if self.original_size != self.current_size:
                        data = cv2.resize(data, dsize=self.current_size, interpolation=self.interp)
                    data = self.post_func(data)

                    self.frame_data = data
                    self.frame_surf = self._create_frame(data)

                    self._frames += 1
                    self._last_tick = time.time()

                    return True

        return False

    def update(self):
        return self._update()

    def set_post_func(self, func: Callable[[np.ndarray], np.ndarray]) -> None:
        self.post_func = func

    def set_interp(self, interp: Union[str, int]) -> None:
        if interp in ("nearest", 0):
            self.interp = cv2.INTER_NEAREST
        elif interp in ("linear", 1):
            self.interp = cv2.INTER_LINEAR
        elif interp in ("area", 3):
            self.interp = cv2.INTER_AREA
        elif interp in ("cubic", 2):
            self.interp = cv2.INTER_CUBIC
        elif interp in ("lanczos4", 4):
            self.interp = cv2.INTER_LANCZOS4
        else:
            raise ValueError("Interpolation technique not recognized.")

    def play(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False
        self.frame_data = None
        self.frame_surf = None

    def resize(self, size: Tuple[int, int]) -> None:
        self.current_size = size

    def change_resolution(self, height: int) -> None:
        self.current_size = (int(height * self.aspect_ratio), height)

    def close(self) -> None:
        self.stop()
        self._vid.release()

    def get_pos(self) -> float:
        return self._frames / self.fps

    def draw(self, surf: pygame.Surface, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(surf, pos)
            return True
        return False

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf, pos):
        surf.blit(self.frame_surf, pos)
    
    def preview(self) -> None:
        win = pygame.display.set_mode(self.current_size)
        pygame.display.set_caption(f"webcam")
        self.play()
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
            pygame.time.wait(60)
            self.draw(win, (0, 0), force_draw=False)
            pygame.display.update()
        pygame.display.quit()
        self.close()

