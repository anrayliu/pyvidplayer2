import tkinter as tk
import numpy as np 
from typing import Callable, Union, Tuple
from .video import Video, READER_AUTO
from .post_processing import PostProcessing


class VideoTkinter(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """
        
    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False, no_audio: bool = False, speed: float = 1, youtube: bool = False, 
                 max_res: int = 720, as_bytes: bool = False, audio_track: int = 0, vfr: bool = False, pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader)

    def _create_frame(self, data):
        h, w = data.shape[:2]
        if self.colour_format == "BGR":
            data = data[...,::-1] # converts to RGB
        return tk.PhotoImage(width=w, height=h, data=f"P6 {w} {h} 255 ".encode() + data.tobytes(), format='PPM')

    def _render_frame(self, canvas, pos):
        canvas.create_image(*pos, image=self.frame_surf)

    def draw(self, surf: tk.Canvas, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        return Video.draw(self, surf, pos, force_draw)
    
    def preview(self, max_fps: int = 60) -> None:
        self.play()
        def update():
            self.draw(canvas, (self.current_size[0] / 2, self.current_size[1] / 2), force_draw=False)
            if self.active:
                root.after(int(1 / float(max_fps) * 1000), update) # for around 60 fps
            else:
                root.destroy()
        root = tk.Tk()
        root.title(f"tkinter - {self.name}")
        canvas = tk.Canvas(root, width=self.current_size[0], height=self.current_size[1], highlightthickness=0)
        canvas.pack()
        update()
        root.mainloop()
        self.close()