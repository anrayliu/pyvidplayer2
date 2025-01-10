'''
This example shows how the audio for any video can be disabled
'''


from pyvidplayer2 import Video


# no_audio will be automatically detected and set for silent videos,
# but you can also use the option to forcefully silence video playback

with Video(r"resources\billiejean.mp4", no_audio=True) as v:
    v.preview()
