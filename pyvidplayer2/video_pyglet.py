import cv2 
import pyglet 
import numpy
from .video import Video
from typing import Tuple
from .post_processing import PostProcessing


class VideoPyglet(Video):
    def __init__(self, path: str, chunk_size=300, max_threads=1, max_chunks=1, interp=cv2.INTER_LINEAR, post_process=PostProcessing.none) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, interp=interp, post_process=post_process)

    def __str__(self) -> str:
        return f"<VideoPyglet(path={self.path})>"

    def _create_frame(self, data: numpy.ndarray) -> pyglet.image.ImageData:
        return pyglet.image.ImageData(*self.current_size, "BGR", cv2.flip(data, 0).tobytes())
    
    def _render_frame(self, pos: Tuple[int, int]) -> None:
        self.frame_surf.blit(*pos)

    def draw(self, pos: Tuple[int, int], force_draw=True) -> bool:
        if self._update() or force_draw:
            if self.frame_surf is not None:
                self._render_frame(pos) # (0, 0) pos draws the video bottomleft
                return True
        return False
    
    def preview(self) -> None:
        def update(dt):
            self.draw((0, 0), force_draw=False)
            if not self.active:
                win.close()
        win = pyglet.window.Window(width=self.current_size[0], height=self.current_size[1], config=pyglet.gl.Config(double_buffer=False), caption=f"pyglet - {self.name}")
        pyglet.clock.schedule_interval(update, 1/60.0)
        pyglet.app.run()
        self.close()