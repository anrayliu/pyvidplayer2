'''
This example shows the 2 ways of seeking
'''

from pyvidplayer2 import Video 


v1 = Video("resources\\billiejean.mp4")

# seek to first minute

v1.seek(60, relative=False)

v1.preview()


v2 = Video("resources\\trailer2.mp4")

# seek to 500th frame 

v2.seek_frame(499, relative=False)

v2.preview()
