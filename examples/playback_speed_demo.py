'''
This example shows how you can control the playback speed of videos
'''


from pyvidplayer2 import Video

v = Video(r"resources\trailer1.mp4", speed=2).preview()   # plays video twice as fast
