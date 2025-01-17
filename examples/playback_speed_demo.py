'''
This example shows how you can control the playback speed of videos
'''


from pyvidplayer2 import Video


# speed is capped between 0.25x and 10x the original speed

with Video(r"resources\trailer1.mp4", speed=2) as v:
    v.preview()   # plays video twice as fast
