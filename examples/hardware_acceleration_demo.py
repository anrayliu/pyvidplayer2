'''
This example demonstrates using NVIDIA hardware acceleration
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video, VideoPlayer, READER_FFMPEG


# use first NVIDIA GPU
# must use FFMPEG_READER
v = Video("resources/ocean.mkv", cuda_device=0, reader=READER_FFMPEG)

player = VideoPlayer(v, (0, 0, *v.current_size), interactable=True)

# hardware acceleration will only improve performance
# when the bottleneck is video decoding (e.g seeking high-resolution videos)
# in python, the bottleneck is usually in rendering the image, not from
# ffmpeg's decoding

player.preview()
