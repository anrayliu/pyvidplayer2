'''
This demo shows how the audio output device can be specified for each video
pip install sounddevice before using
'''

from pyvidplayer2 import Video 
import sounddevice


# find the index of the device you want

# e.g
# 0 Microsoft Sound Mapper - Input, MME (2 in, 0 out)
# 1 Microsoft Sound Mapper - Output, MME (0 in, 2 out)


print(sounddevice.query_devices())


# replace None with the index of the chosen device (first number listed by sd)

Video("resources\\trailer1.mp4", audio_index=None).preview()
