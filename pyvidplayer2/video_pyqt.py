import cv2
import numpy
from .video import Video
from typing import Tuple
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import QTimer
from .post_processing import PostProcessing


class VideoPyQT(Video):
    def __init__(self, path: str, chunk_size=300, max_threads=1, max_chunks=1, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=False) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio)

    def __str__(self) -> str:
        return f"<VideoPyQT(path={self.path})>"

    def _create_frame(self, data: numpy.ndarray) -> QImage:
        return QImage(data, data.shape[1], data.shape[0], data.strides[0], QImage.Format.Format_BGR888)

    def _render_frame(self, win: QMainWindow, pos: Tuple[int, int]) -> None: #must be called in paintEvent
        QPainter(win).drawPixmap(*pos, QPixmap.fromImage(self.frame_surf))

    def preview(self) -> None:
        class Window(QMainWindow):
            def __init__(self):
                super().__init__()
                self.canvas = QWidget(self)
                self.setCentralWidget(self.canvas)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update)
                self.timer.start(16)
            def paintEvent(self_, _):
                self.draw(self_, (0, 0))
        app = QApplication([])
        win = Window()
        win.setWindowTitle(f"pyqt6 - {self.name}")
        win.setFixedSize(*self.current_size)
        win.show()
        app.exec()
        self.close()
