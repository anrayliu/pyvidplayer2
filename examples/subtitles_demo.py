from pyvidplayer2 import Subtitles, Video

Video(r"resources\trailer.mp4", subs=Subtitles(r"resources\subs.srt")).preview()