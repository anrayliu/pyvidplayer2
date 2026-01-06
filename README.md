![logo](logo.png)

[![PyPI Version](https://img.shields.io/pypi/v/pyvidplayer2?logo=pypi&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![PyPI Downloads](https://static.pepy.tech/badge/pyvidplayer2)](https://pepy.tech/projects/pyvidplayer2)
[![Status](https://img.shields.io/pypi/status/pyvidplayer2)](https://pypi.org/project/pyvidplayer2/)
![Coverage](https://img.shields.io/badge/Coverage-96%25-red)
[![Python Version](https://img.shields.io/pypi/pyversions/pyvidplayer2?logo=python&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anrayliu/pyvidplayer2)
[![Made with ❤️](https://img.shields.io/badge/Made_with-❤️-blue?style=round-square)](https://github.com/anrayliu/pyvidplayer2)

Introducing pyvidplayer2, the successor to pyvidplayer. It's better in
pretty much every way, and finally allows an easy way to play videos in Python.
Please note that this library is currently under development, so if you encounter a bug or a video that cannot be
played, please open an issue at https://github.com/anrayliu/pyvidplayer2/issues.

All the features from the original library have been ported over, with the exception of `alt_resize()`. Since
pyvidplayer2 has a completely revamped foundation, the unreliability of `set_size()` has been quashed, and a fallback
function is now redundant.

# Features (see examples folder)

- Easy to implement (4 lines of code)
- Only essential dependencies are numpy, FFmpeg + FFprobe (cv2 is just nice to have)
- Fast and reliable
- Low CPU usage
- No audio/video sync issues
- Unlocked frame rate
- Nvidia hardware acceleration (AMD coming soon)
- Supports GIFs!
- Can play a huge variety of video formats
- Play variable frame rate videos (VFR)
- Adjust playback speed
- Reverse playback
- Subtitle support (.srt, .ass, etc)
- Play multiple videos in parallel
- Add multiple subtitles to a video
- Built in GUI and queue system
- Support for Pygame, PygameCE, Pyglet, Tkinter, PySide6, PyQT6, and Raylib
- Post process effects
- Webcam feed
- Stream videos from Youtube
- Grab subtitles from Youtube, including automatic generation and translation
- Play videos as byte objects
- Specify which audio devices to use
- Frame-by-frame iteration
- Choose audio different audio tracks
- Seamless video looping

# Installation

## Windows

```
pip install pyvidplayer2
```

Note: FFmpeg (just the essentials is fine) must be installed and accessible via the system PATH. Here's an online
article on how to do this (windows):
https://phoenixnap.com/kb/ffmpeg-windows.
FFprobe may also be needed for certain features - this should come bundled with the FFmpeg download.

## Linux

Before running `pip install pyvidplayer2`, you must first install the required development packages.

- Ubuntu/Debian example: `sudo apt install build-essential python3-dev portaudio19-dev libjack-jackd2-dev`
    - The Python and PortAudio development packages prevent missing Python.h and missing portaudio.h errors,
      respectively.
    - Installing `libjack-jackd2-dev` manually prevents `portaudio19-dev` from downgrading to libjack0 and removing wine
      etc (<https://bugs.launchpad.net/ubuntu/+source/portaudio19/+bug/132002>).
    - In some circumstances, such as if you are using the kxstudio repo with Linux Mint, incompatible packages may be
      removed (See <https://github.com/anrayliu/pyvidplayer2/issues/36> for the latest updates on this issue):

```
The following additional packages will be installed:
  libjack-dev libjack0 libportaudiocpp0
Suggested packages:
  jackd1 portaudio19-doc
The following packages will be REMOVED:
  libasound2-plugins:i386 libjack-jackd2-0 libjack-jackd2-0:i386 wine-stable wine-stable-i386:i386 winehq-stable
The following NEW packages will be installed:
  libjack-dev libjack0 libportaudiocpp0 portaudio19-dev
```

## MacOS

FFmpeg can easily be installed with homebrew. Portaudio is also required to prevent missing portaudio.h errors.

```
brew install ffmpeg portaudio
```

# Dependencies

```
numpy
FFmpeg and FFprobe (not Python packages)
```

## Optional Packages

At least one graphics library and one audio library is required.
Use `pip install pyvidplayer2[all]` to install everything.

```
opencv_python   (efficiency improvements and more features, comes installed)
pygame-ce       (graphics and audio library, comes installed)
PyAudio         (better audio library, comes installed)
pysubs2         (for subtitles, comes installed)
yt_dlp          (for streaming Youtube videos)
decord          (for videos in bytes, best option)
imageio         (for videos in bytes)
av              (required for imageio)
pyglet          (graphics library)
PySide6         (graphics library)
PyQt6           (graphics library)
tkinter         (graphics library, installed through Python, not pip)
raylib          (graphics library)
```

# Quickstart

Refer to the examples folder for more basic guides, and documentation.md contains more detailed information.

## Super Quick Demo

```
from pyvidplayer2 import Video
Video("video.mp4").preview()
```

## Pygame Integration

Refer to the examples folder for integration with other graphics libraries.

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

# Known Bugs

For a list of known bugs, refer to https://github.com/anrayliu/pyvidplayer2/issues/53.
If you see an issue not listed, feel free to open an issues page!

# Documentation

To get started quickly, you can browse the many [code examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples).
For more detailed information, read the [documentation](https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md).
If you prefer natural language, try asking [DeepWiki](https://deepwiki.com/anrayliu/pyvidplayer2). Finally, if you still have questions, 
open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues) or email me at `anrayliu@gmail.com`. I'm more than happy to answer!