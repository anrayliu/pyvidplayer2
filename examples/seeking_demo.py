'''
This example shows the two ways of seeking
'''

from pyvidplayer2 import Video 


with Video("resources\\billiejean.mp4") as v:
    # skip ahead 60 seconds
    # accepts floats as well

    v.seek(60, relative=True)
    v.preview()


with Video("resources\\trailer2.mp4") as v:

    # seek to 500th frame

    v.seek_frame(499, relative=False)
    v.preview()
