import pyglet
import numpy as np
from typing import Union, Callable, Tuple
from .video import Video, READER_AUTO
from .post_processing import PostProcessing


class VideoPyglet(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """

        
    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False, no_audio: bool = False, speed: float = 1, youtube: bool = False, 
                 max_res: int = 720, as_bytes: bool = False, audio_track: int = 0, vfr: bool = False, pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader)

    def _create_frame(self, data):
        return pyglet.image.ImageData(*self.current_size, self._vid._colour_format, np.flip(data, 0).tobytes())
    
    def _render_frame(self, pos):
        self.frame_surf.blit(*pos)

    def draw(self, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(pos) # (0, 0) pos draws the video bottomleft
            return True
        return False
    
    def preview(self, max_fps: int = 60) -> None:
        self.play()
        def update(dt):
            self.draw((0, 0), force_draw=True)
            if not self.active:
                win.close()
        win = pyglet.window.Window(width=self.current_size[0], height=self.current_size[1], config=pyglet.gl.Config(double_buffer=True), caption=f"pyglet - {self.name}")
        pyglet.clock.schedule_interval(update, 1/float(max_fps))
        pyglet.app.run()
        self.close()