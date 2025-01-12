'''
This example shows how you can choose the audio track to play in a video
'''


from pyvidplayer2 import Video


# audio_track = 0 will choose the first track, = 1 will choose the second, and so on

with Video(r"your_video_with_multiple_audio_tracks", audio_track=0) as v:
    v.preview()
