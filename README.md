![logo](logo.png)

[![PyPI Version](https://img.shields.io/pypi/v/pyvidplayer2?logo=pypi&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![PyPI Downloads](https://static.pepy.tech/badge/pyvidplayer2)](https://pepy.tech/projects/pyvidplayer2)
[![Status](https://img.shields.io/pypi/status/pyvidplayer2)](https://pypi.org/project/pyvidplayer2/)
![Coverage](https://img.shields.io/badge/Coverage-96%25-red)
[![Python Version](https://img.shields.io/pypi/pyversions/pyvidplayer2?logo=python&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anrayliu/pyvidplayer2)
[![Made with ❤️](https://img.shields.io/badge/Made_with-❤️-blue?style=round-square)](https://github.com/anrayliu/pyvidplayer2)

Striving to be the most comprehensive video playback library for Python.

Note that this library is under active development. If you encounter a bug or a video that cannot be
played, please open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues).

# Features

- Easy to implement (4 lines of code)
- Only essential dependencies are numpy, FFmpeg + FFprobe
- Fast and efficient
- No audio/video sync issues
- Unlocked frame rate
- Nvidia hardware acceleration (AMD coming later)
- Supports GIFs!
- Supports almost any video codec and container
- Play variable frame rate videos (VFR)
- Adjust playback speed
- Reverse playback
- Subtitle support (.srt, .ass, etc)
- Play multiple videos in parallel
- Add multiple subtitles to a video
- Built in GUI and queue system
- Support for Pygame, PygameCE, Pyglet, Tkinter, PySide6, PyQT6, Raylib, and wxPython
- Post process effects
- Webcam feed
- Stream videos from Youtube
- Grab subtitles from Youtube, including automatic generation and translation
- Play videos as byte objects
- Specify output devices
- Frame-by-frame iteration
- Specify different audio tracks
- Seamless video looping

# Installation

Install with pip.
```
pip install pyvidplayer2
```
In addition, FFmpeg and FFprobe must be downloaded and accessible via PATH.
Downloading FFmpeg usually also downloads FFprobe.

## Windows

Go to the [official FFmpeg website](https://www.ffmpeg.org/) to download FFmpeg.
Add the bin folder location to the PATH environment variable. There's plenty of tutorials online for this.

## Linux

Before running `pip install pyvidplayer2`, use your package manager to install some system
packages. FFmpeg is also installed this way, and it should be accessible via $PATH by default.

- Ubuntu/Debian: `sudo apt install ffmpeg python3-dev libjack-jackd2-dev portaudio19-dev`
- Fedora/RHEL: `sudo dnf install ffmpeg python3-devel portaudio-devel`

## MacOS

Before running `pip install pyvidplayer2`, install PortAudio and FFmpeg with homebrew.
Limited testing was done on this platform, so please report any issues.

```
brew install ffmpeg portaudio
```

# Dependencies

```
numpy
FFmpeg and FFprobe (binaries, not Python packages)
```

## Optional Packages

At least one graphics library and one audio library is required.

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
tkinter         (graphics library, installed as a system package or with Python installer, not pip)
raylib          (graphics library)
wxPython        (graphics library)
```

Use `pip install pyvidplayer2[all]` to install all packages required for running the unit tests.
Not required or recommended for regular users.

# Quickstart

Refer to the [examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples) folder for more basic examples.

## Super Quick Demo

```
from pyvidplayer2 import Video
Video("video.mp4").preview()
```

## Pygame Integration

Refer to the [examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples) folder for integrations with other graphics libraries.

```
import pygame
from pyvidplayer2 import Video


# Create video object

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
        vid.restart()           # Rewind video to beginning
    elif key == "p":
        vid.toggle_pause()      # Pause/play video
    elif key == "m":
        vid.toggle_mute()       # Mute/unmute video
    elif key == "right":
        vid.seek(15)            # Skip 15 seconds in video
    elif key == "left":
        vid.seek(-15)           # Rewind 15 seconds in video
    elif key == "up":
        vid.set_volume(1.0)     # Max volume
    elif key == "down":
        vid.set_volume(0.0)     # Min volume

    # Only draw new frames, and only update the screen if something is drawn

    if vid.draw(win, (0, 0), force_draw=False):
        pygame.display.update()

    pygame.time.wait(16)


# Close video when done

vid.close()
pygame.quit()
```

# Documentation

To get started quickly, you can browse the many [code examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples).
For more detailed information, read the [documentation](https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md).
If you prefer natural language, try asking [DeepWiki](https://deepwiki.com/anrayliu/pyvidplayer2). Finally, if you still have questions, 
open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues) or email me at `anrayliu@gmail.com`. I'm more than happy to answer!

# Known Bugs

For a list of known bugs, refer to [this page](https://github.com/anrayliu/pyvidplayer2/issues/53).
If you see an issue not listed, feel free to open a new issue!
