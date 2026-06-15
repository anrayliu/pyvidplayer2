'''
This example shows the different ways of seeking
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video

with Video("resources/billiejean.mp4") as v:
    # skip ahead 60 seconds
    # accepts floats as well

    v.seek(60, relative=True)
    v.preview()


with Video("resources/trailer2.mp4") as v:

    # seek to 500th frame

    v.seek_frame(499, relative=False)
    v.preview()


# can also access frames by index
# this only temporarily fetches the frame, does not interrupt playback

with Video("resources/birds.avi") as v:
    print(v[99]) # 100th frame

    v.preview()
