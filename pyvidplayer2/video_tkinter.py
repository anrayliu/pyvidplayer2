import pygame
import cv2
import numpy
import tkinter
from .video import Video
from typing import Tuple
from .post_processing import PostProcessing


class VideoTkinter(Video):
    def __init__(self, path: str, chunk_size=300, max_threads=1, max_chunks=1, interp=cv2.INTER_LINEAR, post_process=PostProcessing.none) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, interp=interp, post_process=post_process)

    def __str__(self) -> str:
        return f"<VideoTkinter(path={self.path})>"

    def _create_frame(self, data: numpy.ndarray) -> tkinter.PhotoImage:
        h, w = data.shape[:2]
        return tkinter.PhotoImage(width=w, height=h, data=f"P6 {w} {h} 255 ".encode() + cv2.cvtColor(data, cv2.COLOR_BGR2RGB).tobytes(), format='PPM')

    def _render_frame(self, surf: pygame.Surface, pos: Tuple[int, int]) -> None:
        surf.create_image(*pos, image=self.frame_surf)

    def preview(self) -> None:
        def update():
            self.draw(canvas, (self.current_size[0] / 2, self.current_size[1] / 2), force_draw=False)
            if self.active:
                root.after(15, update) # for around 60 fps
            else:
                root.destroy()
        root = tkinter.Tk()
        root.title(f"tkinter - {self.name}")
        canvas = tkinter.Canvas(root, width=self.current_size[0], height=self.current_size[1], highlightthickness=0)
        canvas.pack()
        update()
        root.mainloop()
        self.close()