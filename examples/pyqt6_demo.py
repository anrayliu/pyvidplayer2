'''
This is a quick example of integrating a video into a pyqt6 project
'''


from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import QTimer
from pyvidplayer2 import VideoPyQT


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = QWidget(self)
        self.setCentralWidget(self.canvas)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def paintEvent(self, _):
        video.draw(self, (0, 0))


video = VideoPyQT(r"resources\trailer1.mp4")

app = QApplication([])
win = Window()
win.setWindowTitle(f"pyqt6 support demo")
win.setFixedSize(*video.current_size)
win.show()
app.exec()

video.close()
