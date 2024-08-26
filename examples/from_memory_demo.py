'''
This example shows how videos can be played from memory instead of disk
pip install imageio before using
'''


from pyvidplayer2 import Video


with open("resources\\ocean.mkv", "rb") as f:
    vid_in_bytes = f.read()        # loads file into memory

    Video(vid_in_bytes, as_bytes=True).preview()