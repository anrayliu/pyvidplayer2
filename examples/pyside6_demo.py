'''
Copy and pasted from the pyqt6 demo, but changed names to pyside6
Pyqt6 and pyside6 have very similar interfaces
'''


from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QTimer
from pyvidplayer2 import VideoPySide


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


video = VideoPySide(r"resources/trailer1.mp4")

app = QApplication([])
win = Window()
win.setWindowTitle(f"pyside6 support demo")
win.setFixedSize(*video.current_size)
win.show()
app.exec()

video.close()
