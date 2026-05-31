class Pyvidplayer2Error(Exception):
    """Base Exception inherited by all pyvidplayer2 exceptions."""


class AudioDeviceError(Pyvidplayer2Error):
    """Thrown for errors related to audio output devices."""


class AudioStreamError(Pyvidplayer2Error):
    """Thrown for errors related to audio tracks within video."""


class SubtitleError(Pyvidplayer2Error):
    """Thrown for errors related to subtitles."""


class VideoStreamError(Pyvidplayer2Error):
    """Thrown for errors related to video probing and playback."""


class FFmpegNotFoundError(Pyvidplayer2Error, FileNotFoundError):
    """Thrown when pyvidplayer2 cannot find FFmpeg or FFprobe."""


class OpenCVError(Pyvidplayer2Error):
    """Thrown for errors originating from OpenCV."""


class YTDLPError(Pyvidplayer2Error):
    """Thrown for errors originating from yt-dlp."""


class WebcamNotFoundError(Pyvidplayer2Error):
    """Thrown when there are no available webcam devices."""
