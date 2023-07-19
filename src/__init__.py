import pygame 
pygame.init()

ffmpeg_path = "ffmpeg"

def get_ffmpeg_path() -> str:
    return ffmpeg_path

def set_ffmpeg_path(path: str) -> None:
    ffmpeg_path = path

from .video import Video
from .post_processing import PostProcessing 
from .parallel_video import ParallelVideo 
from .video_player import VideoPlayer 
from .video_collection import VideoCollection

try:
    import PIL
except ImportError:
    pass 
else:
    from .video_tkinter import VideoTkinter

try:
    import srt 
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