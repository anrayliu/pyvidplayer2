'''
This example shows how to play vfr videos
Unfortunately, none of the example videos are vfr - try using your own!
'''

from pyvidplayer2 import Video

v = Video("resources\\billiejean.mp4", vfr=True)

print(v.min_fr)
print(v.max_fr)
print(v.avg_fr)

v.preview()
