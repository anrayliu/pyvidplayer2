'''
This example shows how the Video object can be used as a generator to iterate through each frame
'''

# Sample videos can be found here: https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video


with Video("resources/clip.mp4") as v:
    for frame in Video("resources/clip.mp4"):

        # each frame is returned as a numpy.ndarray

        print(frame.shape)
