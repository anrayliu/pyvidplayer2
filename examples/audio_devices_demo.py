'''
This demo shows how the audio output device can be specified for each video
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources

from pprint import pprint
import sounddevice
from pyvidplayer2 import Video

# FOR PYGAME
# Changing the output device is not related to pyvidplayer2
# Refer to https://stackoverflow.com/questions/57099246/set-output-device-for-pygame-mixer
# to see how the output device can be specified during mixer initialization

# FOR SOUNDDEVICE

# find the index of the device you want
# not all hostapis work well. I've found success with
# MME and WASAPI (v0.9.34+), but your experience may vary

# e.g
# 0 Microsoft Sound Mapper - Input, MME (2 in, 0 out)
# 1 Microsoft Sound Mapper - Output, MME (0 in, 2 out)

print("Host APIs:\n")
pprint(sounddevice.query_hostapis())

print("\nDevices:\n")
print(sounddevice.query_devices())

# replace None with the index of the chosen device (first number listed by sd)
# e.g Video("resources/trailer1.mp4", audio_index=0).preview()

with Video("resources/trailer1.mp4", audio_index=None) as v:
    v.preview()
