import cv2 
import pygame 
import numpy
from .video import Video
from typing import Tuple
from .post_processing import PostProcessing


class VideoPygame(Video):
    def __init__(self, path: str, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp)

    def __str__(self) -> str:
        return f"<VideoPygame(path={self.path})>"

    def _create_frame(self, data: numpy.ndarray) -> pygame.Surface:
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf: pygame.Surface, pos: Tuple[int, int]) -> None:
        surf.blit(self.frame_surf, pos)
    
    def preview(self) -> None:
        pygame.init()
        win = pygame.display.set_mode(self.current_size)
        pygame.display.set_caption(f"pygame - {self.name}")
        self.play()
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active = False
            pygame.time.wait(16)
            self.draw(win, (0, 0), force_draw=False)
            pygame.display.update()
        pygame.display.quit()
        self.close()