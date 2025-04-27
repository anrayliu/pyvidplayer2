'''
This example shows how to play vfr videos
Unfortunately, none of the example videos are vfr - try using your own!
'''

# Sample videos can be found here: https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video


# normal videos can still be playedin vfr mode

v = Video("resources/billiejean.mp4", vfr=True)

print(v.min_fr)
print(v.max_fr)
print(v.avg_fr)

v.preview()
