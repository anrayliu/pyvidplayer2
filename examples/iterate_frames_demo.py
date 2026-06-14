'''
This example shows how the Video object can be used as a generator to iterate
through each frame
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video
from matplotlib import pyplot as plt  # pip install matplotlib

with Video("resources/clip.mp4") as v:
    for frame in v:
        if v.frame == 80:
            break
        # each frame is returned as a numpy.ndarray
        print(frame.shape)

    # display frame
    plt.imshow(frame)
    plt.show()

    # video playback continues from last frame position
    v.preview()
