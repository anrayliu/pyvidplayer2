'''
This is an example showing how to add subtitles to a video
'''


from pyvidplayer2 import Subtitles, Video

Video(r"resources\trailer2.mp4", subs=Subtitles(r"resources\subs2.srt")).preview()