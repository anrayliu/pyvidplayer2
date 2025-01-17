'''
This example shows how to stream videos from youtube in 720p
pip install yt-dlp before using
'''

from pyvidplayer2 import Video


# chunk_size must be at least 60 for a smooth experience
# max_threads is forced to 1

Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=480, chunk_size=60).preview()

# increasing chunks_size is better for long videos

Video("https://www.youtube.com/watch?v=KJwYBJMSbPI&t=1s", youtube=True, max_res=720, chunk_size=300).preview()
