'''
This is an example of the cel shading post process you can apply to your videos
'''

from pyvidplayer2 import Video, PostProcessing

Video(r"resources\medic.mov", post_process=PostProcessing.cel_shading).preview()