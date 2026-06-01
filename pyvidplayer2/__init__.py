import importlib.util

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


from .error import (AudioDeviceError, AudioStreamError, FFmpegNotFoundError,
                    OpenCVError, Pyvidplayer2Error, SubtitleError,
                    VideoStreamError, WebcamNotFoundError, YTDLPError)
from .post_processing import PostProcessing
from .video import (READER_AUTO, READER_DECORD, READER_FFMPEG, READER_IMAGEIO,
                    READER_OPENCV)


if importlib.util.find_spec("tkinter") is not None:
    from .video_tkinter import VideoTkinter

if importlib.util.find_spec("PySide6") is not None:
    from .video_pyside import VideoPySide

if importlib.util.find_spec("PyQt6") is not None:
    from .video_pyqt import VideoPyQT

if importlib.util.find_spec("pyray") is not None:
    from .video_raylib import VideoRaylib

if importlib.util.find_spec("wx") is not None:
    from .video_wx import VideoWx

if importlib.util.find_spec("pyglet") is not None:
    from .video_pyglet import VideoPyglet

if importlib.util.find_spec("pygame") is not None:
    # bug on linux: importing pygame before decord results
    # in display.set_mode deadlocking
    try:
        import decord
    except ImportError:
        pass

    import pygame

    pygame.init()

    # isort will try and change the order of these 2 imports,
    # but doing so will cause a circular import
    # keep in current order!
    # --------------------------------------------
    from .video_pygame import VideoPygame as Video
    from .video_player import VideoPlayer
    # --------------------------------------------

    if importlib.util.find_spec("cv2") is not None:
        from .webcam import Webcam

    if importlib.util.find_spec("pysubs2") is not None:
        from .subtitles import Subtitles

# cv2.setLogLevel(0) # silent

from subprocess import run


def get_version_info():
    try:
        pygame_ver = pygame.version.ver
    except NameError:
        pygame_ver = "not installed"

    try:
        ffmpeg_ver = run([get_ffmpeg_path(), "-version"],
                         capture_output=True,
                         universal_newlines=True,
                         check=False).stdout.split(" ")[2]
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
