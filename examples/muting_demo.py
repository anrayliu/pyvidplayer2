'''
This example shows how the audio for any video can be disabled
'''


from pyvidplayer2 import Video

Video(r"resources\billiejean.mp4", no_audio=True).preview()
