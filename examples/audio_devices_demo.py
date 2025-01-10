'''
This demo shows how the audio output device can be specified for each video
pip install sounddevice before using
'''

from pyvidplayer2 import Video 
import sounddevice

# FOR PYGAME
# Changing the output device is not related to pyvidplayer2
# Refer to https://stackoverflow.com/questions/57099246/set-output-device-for-pygame-mixer to see how the output device
# can be specified during mixer initialization

# FOR PYAUDIO
# see instructions below

# find the index of the device you want
# not all hostapis work, but MME for Windows should be fine

# e.g
# 0 Microsoft Sound Mapper - Input, MME (2 in, 0 out)
# 1 Microsoft Sound Mapper - Output, MME (0 in, 2 out)


print(sounddevice.query_devices())


# replace None with the index of the chosen device (first number listed by sd)
# e.g Video("resources\\trailer1.mp4", audio_index=0).preview()

with Video("resources\\trailer1.mp4", audio_index=None) as v:
    v.preview()
