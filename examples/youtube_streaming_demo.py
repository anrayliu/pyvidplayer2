'''
This example shows how to stream videos from youtube in 720p
pip install yt-dlp[default] opencv-python before using

**********************************************************************************************************
Unfortunately, changes to YouTube over time have made this feature significantly less reliable than before

In addition, yt-dlp was forced to make some sweeping changes in late 2025
To use this feature, you must follow the steps outlined here: https://github.com/yt-dlp/yt-dlp/wiki/EJS
**********************************************************************************************************
'''


from pyvidplayer2 import Video


# chunk_size must be at least 60 for a smooth experience
# max_threads is forced to 1

Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=720, chunk_size=60).preview()

'''
***************************************************************
Changes to YouTube seem to have broken playback for long videos
***************************************************************
'''

# increasing chunks_size is better for long videos

# Video("https://www.youtube.com/watch?v=KJwYBJMSbPI&t=1s", youtube=True, max_res=720, chunk_size=300).preview()
