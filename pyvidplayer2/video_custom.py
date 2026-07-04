from typing import Callable, Union, override

import numpy as np

from .post_processing import PostProcessing
from .video import READER_AUTO, Video


class VideoCustom(Video):
    """Video playback class with no graphics library integration."""

    def __init__(self, path: Union[str, bytes], chunk_size: float = 10,
                 max_threads: int = 1, max_chunks: int = 1,
                 post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear",
                 use_pygame_audio: bool = False, reverse: bool = False,
                 no_audio: bool = False, speed: float = 1,
                 youtube: bool = False,
                 max_res: int = 720, as_bytes: bool = False,
                 audio_track: int = 0, vfr: bool = False,
                 pref_lang: str = "en", audio_index: int = None,
                 reader: int = READER_AUTO,
                 cuda_device: int = -1) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None,
                       post_process, interp, use_pygame_audio,
                       reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index,
                       reader, cuda_device)

    def _create_frame(self, data):
        return None

    def _render_frame(self, *args):
        pass

    @override
    def draw(self, *args, **kwargs) -> bool:
        return Video.draw(self, None, None, False)

    def preview(self, *args, **kwargs) -> None:
        pass
