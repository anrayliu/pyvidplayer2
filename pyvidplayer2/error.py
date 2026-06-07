class Pyvidplayer2Error(Exception):
    """Base exception for pyvidplayer2 related exceptions."""


class AudioDeviceError(Pyvidplayer2Error):
    """Thrown for errors related to Sounddevice output devices."""


class AudioStreamError(Pyvidplayer2Error):
    """Thrown for errors related to audio tracks."""


class SubtitleError(Pyvidplayer2Error):
    """Thrown for errors related to subtitles."""


class VideoStreamError(Pyvidplayer2Error):
    """Thrown for errors related to general video probing and playback."""


class FFmpegNotFoundError(Pyvidplayer2Error, FileNotFoundError):
    """Thrown when FFmpeg is missing."""


class OpenCVError(Pyvidplayer2Error):
    """Thrown for errors related to OpenCV processes."""


class YTDLPError(Pyvidplayer2Error):
    """Thrown for errors related to YTDLP processes."""


class WebcamNotFoundError(Pyvidplayer2Error):
    """Thrown when there are no webcams to activate."""
