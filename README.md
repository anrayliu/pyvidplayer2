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

# Quickstart

Refer to the examples folder for more basic guides, and documentation.md contains more detailed information.

```
import pygame
from pyvidplayer2 import Video


# create video object

vid = Video("video.mp4")

win = pygame.display.set_mode(vid.current_size)
pygame.display.set_caption(vid.name)


while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    if key == "r":
        vid.restart()           #rewind video to beginning
    elif key == "p":
        vid.toggle_pause()      #pause/plays video
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

```