'''
This example shows how to stream videos from youtube in 720p
pip install yt-dlp before using
Beta feature, might be buggy
'''

from pyvidplayer2 import Video


# use the configuration chunk_size=60+, max_threads=1, max_chunks=1

Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=480, chunk_size=60, max_threads=1, max_chunks=1).preview()

# increasing chunks_size is better for long videos

Video("https://www.youtube.com/watch?v=KJwYBJMSbPI&t=1s", youtube=True, max_res=720, chunk_size=300, max_threads=1, max_chunks=1).preview()
