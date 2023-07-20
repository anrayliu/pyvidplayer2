from pyvidplayer2 import Video, PostProcessing

Video(r"resources\trailer.mp4", post_process=PostProcessing.cel_shading).preview()