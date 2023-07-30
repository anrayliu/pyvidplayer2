ffmpeg_path = "ffmpeg"

def get_ffmpeg_path() -> str:
    return ffmpeg_path

def set_ffmpeg_path(path: str) -> None:
    global ffmpeg_path
    ffmpeg_path = path


from .post_processing import PostProcessing 
from .video_tkinter import VideoTkinter

try:
    import PyQt6
except ImportError:
    pass 
else:
    from .video_pyqt import VideoPyQT

try:
    import pygame
except ImportError:
    pass 
else:
    pygame.init()

    from .video_pygame import VideoPygame as Video
    from .subtitles import Subtitles
    from .video_player import VideoPlayer

try:
    import pyglet
except ImportError:
    pass 
else:
    from .video_pyglet import VideoPyglet