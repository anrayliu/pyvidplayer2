from pyvidplayer2._version import __version__

VERSION = __version__  # for older versions of pyvidplayer2

_ffmpeg_loglvl = "quiet"
_ffmpeg_path = "ffmpeg"
_ffprobe_path = "ffprobe"

##################################################
# need to be near top so library can import these
def get_ffmpeg_loglevel() -> str:
    return _ffmpeg_loglvl

def get_ffmpeg_path() -> str:
    return _ffmpeg_path

def get_ffprobe_path() -> str:
    return _ffprobe_path
##################################################

# bug on linux: importing pygame before decord results
# in display.set_mode deadlocking
try:
    import decord
except ImportError:
    pass

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
    import PyQt6
except ImportError:
    pass
else:
    from .video_pyqt import VideoPyQT

try:
    import pyray
except ImportError:
    pass
else:
    from .video_raylib import VideoRaylib

try:
    import wx
except ImportError:
    pass
else:
    from .video_wx import VideoWx

try:
    import pyglet
except ImportError:
    pass
else:
    from .video_pyglet import VideoPyglet

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


# cv2.setLogLevel(0) # silent

from subprocess import run


def get_version_info():
    try:
        pygame_ver = pygame.version.ver
    except NameError:
        pygame_ver = "not installed"

    try:
        ffmpeg_ver = run([get_ffmpeg_path(), "-version"], capture_output=True, universal_newlines=True).stdout.split(" ")[2]
    except FileNotFoundError:
        ffmpeg_ver = "not installed"

    return {"pyvidplayer2": __version__,
            "ffmpeg": ffmpeg_ver,
            "pygame": pygame_ver}


def set_ffmpeg_loglevel(level: str) -> None:
    global _ffmpeg_loglvl
    if level in (
        "quiet",
        "panic",
        "fatal",
        "error",
        "warning",
        "info",
        "verbose",
        "debug",
        "trace"
    ): _ffmpeg_loglvl = level

def set_ffmpeg_path(path: str) -> None:
    global _ffmpeg_path
    _ffmpeg_path = path

def set_ffprobe_path(path: str) -> None:
    global _ffprobe_path
    _ffprobe_path = path
