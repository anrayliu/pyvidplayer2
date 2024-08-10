[![downloads](https://static.pepy.tech/badge/pyvidplayer2)](http://pepy.tech/project/pyvidplayer2)

# pyvidplayer2 (please report all bugs!)
Languages: English | [中文](https://github.com/anrayliu/pyvidplayer2/blob/main/README.cn.md)


Introducing pyvidplayer2, the successor to pyvidplayer. It's better in
pretty much every way, and finally allows an easy and reliable way to play videos in Python.

All the features from the original library have been ported over, with the exception of ```alt_resize()```. Since pyvidplayer2 has a completely revamped foundation, the unreliability of ```set_size()``` has been quashed, and a fallback function is now redundant.

# Features (tested on Windows)
- Easy to implement (4 lines of code)
- Fast and reliable
- Stream videos from Youtube
- Adjust playback speed
- Reverse playback
- No audio/video sync issues
- Subtitle support (.srt, .ass, etc)
- Play multiple videos in parallel
- Built in GUI
- Support for Pygame, Pyglet, Tkinter, and PyQT6
- Can play all ffmpeg supported video formats
- Post process effects
- Webcam feed

# Installation
```
pip install pyvidplayer2
```
Note: FFMPEG (just the essentials is fine) must be installed and accessible via the system PATH. Here's an online article on how to do this (windows):
https://phoenixnap.com/kb/ffmpeg-windows.

## Linux
Before running `pip install pyvidplayer2`, you must first install the required development packages.
- Ubuntu/Debian example: `sudo apt-get install build-essential python3-dev portaudio19-dev`
  - The Python and PortAudio development packages prevent missing Python.h and missing portaudio.h errors, respectively.

# Quickstart

Refer to the examples folder for more basic guides, and documentation.md contains more detailed information.

```
import pygame
from pyvidplayer2 import Video


# create video object

vid = Video("video.mp4")

win = pygame.display.set_mode(vid.current_size)
pygame.display.set_caption(vid.name)


while vid.active:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.stop()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    if key == "r":
        vid.restart()           #rewind video to beginning
    elif key == "p":
        vid.toggle_pause()      #pause/plays video
    elif key == "m":
        vid.toggle_mute()       #mutes/unmutes video
    elif key == "right":
        vid.seek(15)            #skip 15 seconds in video
    elif key == "left":
        vid.seek(-15)           #rewind 15 seconds in video
    elif key == "up":
        vid.set_volume(1.0)     #max volume
    elif key == "down":
        vid.set_volume(0.0)     #min volume

    # only draw new frames, and only update the screen if something is drawn
    
    if vid.draw(win, (0, 0), force_draw=False):
        pygame.display.update()

    pygame.time.wait(16) # around 60 fps


# close video when done

vid.close()
pygame.quit()

```

Documentation also available in repository as documentation.md.

