'''
This is an example of custom subtitle fonts
pip install pysubs2 before using
'''


from pyvidplayer2 import Subtitles, Video
from pygame.font import Font

subtitles = Subtitles(r"resources\subs2.srt", font=Font(r"resources\font.ttf", 60), highlight=(255, 0, 0, 128), offset=500)

Video(r"resources\trailer2.mp4", subs=subtitles).preview()