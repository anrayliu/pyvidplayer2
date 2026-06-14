'''
This example shows how videos can be played from memory instead of disk
install decord or imageio before using
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import Video

with open("resources/ocean.mkv", "rb") as f:
    with Video(f.read(), as_bytes=True) as v:

        # with no file name, these will be empty strings
        print(v.name, v.ext)

        v.preview()
