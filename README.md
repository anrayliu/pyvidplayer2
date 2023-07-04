# pyvidplayer2
Introducing pyvidplayer2, the successor to pyvidplayer. It's better in
pretty much every way, and finally allows a fast and reliable way to play 
videos in python.

The old example still works with this version.

# **Example**
```
import pygame
from pyvidplayer2 import Video

pygame.init()
win = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

#provide video class with the path to your video
vid = Video("vid.mp4")

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    #your program frame rate does not affect video playback
    clock.tick(60)
    
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
        
    #draws the video to the given surface, at the given position
    vid.draw(win, (0, 0), force_draw=False)
    
    pygame.display.update()
```

This new version retires the unreliable ffpyplayer, and instead uses ffmpeg
for audio and opencv for video.

All the properties and methods from the first pyvidplayer have been retained,
except for these two:

 - ```get_paused()``` - Can now be accessed as a property
 - ```alt_resize``` - Obsolete

# Arguments
The ```Video``` class now has a couple new arguments. Usually they can be left to their default values.

- ```path``` - location of video file
- ```chunk_size = 1``` - audio is loaded into 1 second files
- ```max_threads = 1``` - at most 1 audio chunk will be loading at any given time
- ```max_chunks = 1``` - the next future audio chunk will be loaded and stored in reserve

# Properties
- ```path```
- ```name```
- ```frame_count```
- ```frame_rate```
- ```duration```
- ```original_size```
- ```current_size```
- ```active``` - becomes false when the video finishes playing
- ```frame_surf``` - current video frame as a pygame surface 
- ```buffering``` - becomes true when audio chunks are still loading
- ```paused```
                     
# Functions
- ```restart()```
- ```set_size(size)``` - the unreliability of this from the first version has been fixed!
- ```set_volume(volume)``` - from 0.0 to 1.0
- ```get_volume()```
- ```toggle_pause()```
- ```pause()```
- ```resume()```
- ```close()``` - releases video resources
- ```get_pos()```          - returns the current time in the video in seconds
- ```seek(time, relative=True)``` - if relative is ```True```, moves forwards or backwards by time in seconds in the video
                                    otherwise, the video seeks to the given time regardless of where it currently is
- ```draw(surf, pos, force_draw=True)``` - draws the current video frame onto the given surface at the given position. If
                                          ```force_draw``` is enabled, a surface will be drawn every time draw is called. If it's
                                          disabled, a surface will only be drawn when a new frame from the video is made which saves cpu
 - ```play()``` - sets ```active``` to ```True``` and starts video playback
 - ```stop()``` - sets ```active``` to ```False``` and stops the video
