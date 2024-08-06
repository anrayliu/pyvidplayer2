import cv2 
import pyglet 
from .video import Video
from .post_processing import PostProcessing


class VideoPyglet(Video):
    def __init__(self, path, chunk_size=10, max_threads=1, max_chunks=1, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=False, reverse=False, no_audio=False, speed=1):
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed)

    def __str__(self):
        return f"<VideoPyglet(path={self.path})>"

    def _create_frame(self, data):
        return pyglet.image.ImageData(*self.current_size, "BGR", cv2.flip(data, 0).tobytes())
    
    def _render_frame(self, pos):
        self.frame_surf.blit(*pos)

    def draw(self, pos, force_draw=True):
        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(pos) # (0, 0) pos draws the video bottomleft
            return True
        return False
    
    def preview(self):
        def update(dt):
            self.draw((0, 0), force_draw=True)
            if not self.active:
                win.close()
        win = pyglet.window.Window(width=self.current_size[0], height=self.current_size[1], config=pyglet.gl.Config(double_buffer=False), caption=f"pyglet - {self.name}")
        pyglet.clock.schedule_interval(update, 1/60.0)
        pyglet.app.run()
        self.close()