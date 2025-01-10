'''
This example shows how the Video object can be used as a generator to iterate through each frame
'''

from pyvidplayer2 import Video


with Video("resources\\clip.mp4") as v:
    for frame in Video("resources\\clip.mp4"):

        # each frame is returned as a numpy.ndarray

        print(frame.shape)
