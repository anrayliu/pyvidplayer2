'''
This example shows how you can choose the audio track to play in a video
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources

from pyvidplayer2 import Video, AudioStreamError

# 0 will choose the first track, 1 will choose the second, and so on

try:
    with Video("resources/manya.mp4", audio_track=0) as v:
        print(f"Audio tracks in video: {v.num_audio_tracks}")
        print(f"Channels in current audio track: {v.audio_channels}")
        v.preview()
except AudioStreamError:
    print("audio track doesn't exist!")
