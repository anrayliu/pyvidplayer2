'''
This example shows how to stream videos from youtube in 720p
'''

from pyvidplayer2 import Video 

# for short videos, default settings are fine
Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=720).preview()

# for long videos (15+ mins), increase chunk_size. avoid increasing max_threads and max_chunks
Video("https://www.youtube.com/watch?v=fWRISvgAygU&t=22s", youtube=True, max_res=720, chunk_size=300).preview()
