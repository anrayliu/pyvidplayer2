'''
This example shows how to play vfr videos
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video

# normal videos can still be played in vfr mode

v = Video("resources/vfr.mp4", vfr=True)

print(v.min_fr)
print(v.max_fr)
print(v.avg_fr)

v.preview()
