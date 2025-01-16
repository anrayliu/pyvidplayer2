import io
import pyray
import numpy as np
from typing import Callable, Union, Tuple
from .video import Video, READER_AUTO
from .post_processing import PostProcessing
from PIL import Image


class VideoRaylib(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """


    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1,
                 post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False,
                 no_audio: bool = False, speed: float = 1, youtube: bool = False,
                 max_res: int = 720, as_bytes: bool = False, audio_track: int = 0, vfr: bool = False,
                 pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio,
                       reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader)

    def _create_frame(self, data):
        if self.frame_surf is not None:
            pyray.unload_texture(self.frame_surf)
        buffer = io.BytesIO()
        Image.fromarray(data[...,::-1]).save(buffer, format="BMP")
        img = pyray.load_image_from_memory(".bmp", buffer.getvalue(), len(buffer.getvalue()))
        texture = pyray.load_texture_from_image(img)
        pyray.unload_image(img)
        return texture

    def _render_frame(self, _, pos):
        pyray.draw_texture(self.frame_surf, *pos, pyray.WHITE)

    def draw(self, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        return Video.draw(self, None, pos, force_draw)

    def preview(self, max_fps: int = 60) -> None:
        pyray.init_window(*self.original_size,f"raylib - {self.name}")
        pyray.set_target_fps(max_fps)
        self.play()
        while not pyray.window_should_close() and self.active:
            pyray.begin_drawing()
            if self.draw((0, 0), force_draw=False):
                pyray.end_drawing()
        if self.frame_surf is not None:
            pyray.unload_texture(self.frame_surf)
        pyray.close_window()
        self.close()

    def close(self) -> None:
        if self.frame_surf is not None:
            pyray.unload_texture(self.frame_surf)
        Video.close(self)
