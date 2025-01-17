import numpy as np
from .video import Video, READER_AUTO
from typing import Callable, Union, Tuple
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import QTimer
from .post_processing import PostProcessing


class VideoPyQT(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """


    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False, no_audio: bool = False, speed: float = 1, youtube: bool = False, 
                 max_res: int = 720, as_bytes: bool = False, audio_track: int = 0, vfr: bool = False, pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader)

    def _create_frame(self, data):
        # only BGR and RGB formats in readers right now
        f = QImage.Format.Format_BGR888 if self.colour_format == "BGR" else QImage.Format.Format_RGB888
        return QImage(data, data.shape[1], data.shape[0], data.strides[0], f)

    def _render_frame(self, win, pos): # must be called in paintEvent
        QPainter(win).drawPixmap(*pos, QPixmap.fromImage(self.frame_surf))

    def draw(self, surf: QWidget, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        return Video.draw(self, surf, pos, force_draw)

    def preview(self, max_fps: int = 60) -> None:
        self.play()
        class Window(QMainWindow):
            def __init__(self):
                super().__init__()
                self.canvas = QWidget(self)
                self.setCentralWidget(self.canvas)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update)
                self.timer.start(int(1 / float(max_fps) * 1000))
            def paintEvent(self_, _):
                self.draw(self_, (0, 0))
                if not self.active:
                    QApplication.quit()
        app = QApplication([])
        win = Window()
        win.setWindowTitle(f"pyqt6 - {self.name}")
        win.setFixedSize(*self.current_size)
        win.show()
        app.exec()
        self.close()
