from pyvidplayer2._version import __version__


VERSION = __version__ # for older versions of pyvidplayer2
FFMPEG_LOGLVL = "quiet"


from subprocess import run
from .video import READER_FFMPEG, READER_DECORD, READER_OPENCV, READER_IMAGEIO, READER_AUTO
from .error import *
from .post_processing import PostProcessing

try:
    import tkinter
except ImportError:
    pass
else:
    from .video_tkinter import VideoTkinter

try:
    import PySide6
except ImportError:
    pass
else:
    from .video_pyside import VideoPySide

try:
    import pyray
except ImportError:
    pass
else:
    from .video_raylib import VideoRaylib

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
    from .video_player import VideoPlayer

    try:
        import cv2 
    except ImportError:
        pass 
    else:
        from .webcam import Webcam

    try:
        import pysubs2
    except ImportError:
        pass 
    else:
        from .subtitles import Subtitles

try:
    import pyglet
except ImportError:
    pass
else:
    from .video_pyglet import VideoPyglet


#cv2.setLogLevel(0) # silent

def get_version_info():
    try:
        pygame_ver = pygame.version.ver
    except NameError:
        pygame_ver = "not installed"

    try:
        ffmpeg_ver = run(["ffmpeg", "-version"], capture_output=True, universal_newlines=True).stdout.split(" ")[2]
    except FileNotFoundError:
        ffmpeg_ver = "not installed"

    return {"pyvidplayer2": __version__,
            "ffmpeg": ffmpeg_ver,
            "pygame": pygame_ver}
