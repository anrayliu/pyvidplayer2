from pyvidplayer2._version import __version__


VERSION = __version__ # for older versions of pyvidplayer2
FFMPEG_LOGLVL = "fatal"


from subprocess import run

from .post_processing import PostProcessing
from .error import Pyvidplayer2Error

try:
    import tkinter
except ImportError:
    pass
else:
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
    from .video_player import VideoPlayer
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
