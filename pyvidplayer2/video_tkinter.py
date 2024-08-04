import cv2
import tkinter
from .video import Video
from .post_processing import PostProcessing


class VideoTkinter(Video):
    def __init__(self, path, chunk_size=10, max_threads=1, max_chunks=1, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=False, reverse=False, no_audio=False, speed=1, youtube=False, quality=0):
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, quality)

    def __str__(self):
        return f"<VideoTkinter(path={self.path})>"

    def _create_frame(self, data):
        h, w = data.shape[:2]
        return tkinter.PhotoImage(width=w, height=h, data=f"P6 {w} {h} 255 ".encode() + cv2.cvtColor(data, cv2.COLOR_BGR2RGB).tobytes(), format='PPM')

    def _render_frame(self, canvas, pos):
        canvas.create_image(*pos, image=self.frame_surf)

    def preview(self):
        def update():
            self.draw(canvas, (self.current_size[0] / 2, self.current_size[1] / 2), force_draw=False)
            if self.active:
                root.after(16, update) # for around 60 fps
            else:
                root.destroy()
        root = tkinter.Tk()
        root.title(f"tkinter - {self.name}")
        canvas = tkinter.Canvas(root, width=self.current_size[0], height=self.current_size[1], highlightthickness=0)
        canvas.pack()
        update()
        root.mainloop()
        self.close()