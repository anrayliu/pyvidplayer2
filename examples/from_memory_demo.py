'''
This example shows how videos can be played from memory instead of disk
pip install decord before using
'''


from pyvidplayer2 import Video


# experimental feature, still a little buggy

with open("resources\\ocean.mkv", "rb") as f:
    vid_in_bytes = f.read()        # loads file into memory
    with Video(vid_in_bytes, as_bytes=True) as v:
        v.preview()
