'''
This example shows how you can control the playback speed of videos
'''


from pyvidplayer2 import Video

v = Video(r"resources\trailer1.mp4")
v.set_speed(2) # twice as fast
v.preview()
