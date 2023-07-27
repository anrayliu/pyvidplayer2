# pyvidplayer2

Introducing pyvidplayer2, the successor to pyvidplayer. It's better in
pretty much every way, and finally allows an easy and reliable way to play videos in Python.

All the features from the original library have been ported over, with the exception of ```alt_resize()```. Since pyvidplayer2 has a completely revamped foundation, the unreliability of ```set_size()``` has been quashed, and a fallback function is now redundant.

# Features
- Easy to implement
- Reliable playback
- Fast load times
- No audio/video sync issues
- Low cpu usage
- Subtitle support
- Play multiple videos in parallel
- Built in GUI
- Support for Pygame, Pyglet, and Tkinter
- Can play all ffmpeg supported video formats
- Post process effects

# Installation
```
pip install pyvidplayer2
```
Note: FFMPEG must be installed and accessible via PATH.

In addition, the package ```srt``` is optional but is required for subtitle support.
```
pip install srt
```