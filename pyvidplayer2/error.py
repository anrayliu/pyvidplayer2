class Pyvidplayer2Error(Exception):
    """Base Exception"""
    pass

class AudioDeviceError(Pyvidplayer2Error):
    pass

class SubtitleError(Pyvidplayer2Error):
    pass

class VideoStreamError(Pyvidplayer2Error):
    pass

class FFmpegNotFoundError(Pyvidplayer2Error, FileNotFoundError):
    pass

class OpenCVError(Pyvidplayer2Error):
    pass

class YTDLPError(Pyvidplayer2Error):
    pass

class WebcamNotFoundError(Pyvidplayer2Error):
    pass
