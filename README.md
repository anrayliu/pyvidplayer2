# pyvidplayer2

[![PyPI Version](https://img.shields.io/pypi/v/pyvidplayer2?logo=pypi&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![PyPI Downloads](https://static.pepy.tech/badge/pyvidplayer2)](https://pepy.tech/projects/pyvidplayer2)
[![Status](https://img.shields.io/pypi/status/pyvidplayer2)](https://pypi.org/project/pyvidplayer2/)
![Coverage](https://img.shields.io/badge/Coverage-96%25-red)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fanrayliu%2Fpyvidplayer2%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anrayliu/pyvidplayer2)
[![Made with ❤️](https://img.shields.io/badge/Made_with-❤️-blue?style=round-square)](https://github.com/anrayliu/pyvidplayer2)

Featureful library for embedding videos into Python apps.

<p align="center">
  <img src="demo.gif" />
</p>

## Features

- Integrates with existing apps with just 4 lines of code
- Almost every dependency is optional
- Full video-support: seamless loops, custom playback speed, reverse playback, parallel playback, and more
- Full audio-support: adjust audio track, output device, volume, and more
- Parse subtitles from files or embedded subtitle tracks
- Supports almost every codec and container, VFR videos, even GIFs
- Stream videos and subtitles directly from YouTube
- Frame-by-frame iteration and inspection
- Integrates with 7 graphics libraries (some features limited to Pygame)
- Built-in video player GUI, post-processing effects, webcam features

## Installation

### Windows
Most users can get set up quickly by running
```
pip install pyvidplayer2[ffmpeg]
```
This installs `pyvidplayer2`, the recommended sound library, and a pre-built FFmpeg binary.
You'll still need a graphics library if you don't already have one (e.g. `pip install pygame-ce` for Pygame users).

This command does not install FFprobe. Most features will still work without FFprobe (only FFmpeg is mandatory),
but some will throw an exception if FFprobe is not installed and accessible via PATH. To download FFmpeg or FFprobe,
go to the [official website](https://www.ffmpeg.org/). Afterwards, add the bin folder to the
PATH environment variable. There's plenty of tutorials online for this. 

If you already have FFmpeg on your system, instead run
```
pip install pyvidplayer2
```
Note: For versions before 0.9.38, `pyvidplayer2[ffmpeg]` does not work, so FFmpeg and FFprobe must be installed manually.

### Linux and MacOS
Install with the following
```
pip install pyvidplayer2
```
Then use your package manager to install FFmpeg, FFprobe, and PortAudio.
 - Ubuntu: `sudo apt install ffmpeg python3-dev libjack-jackd2-dev portaudio19-dev`
 - MacOS: `brew install portaudio ffmpeg`

## Dependencies

The only mandatory dependencies are `numpy`, an FFmpeg binary, and a sound and graphics library of your choice.
Every other dependency can be uninstalled and basic video playback will still work. That said, `opencv_python` and
`sounddevice` are highly recommended and are installed by default. FFprobe is also recommended to be installed
alongside FFmpeg (see above installation instructions).

### Optional Packages

```
opencv_python       (backend video reader, efficiency improvements, and enables many features)
decord              (backend video reader)
imageio[pyav]       (backend video reader)
sounddevice         (recommended audio library)
pygame/pygame-ce    (graphics and audio library)
pysubs2             (enables subtitles)
yt_dlp[default]     (enables YouTube streaming)
pyglet              (graphics library)
PySide6             (graphics library)
PyQt6               (graphics library)
tkinter             (graphics library)
raylib              (graphics library)
wxPython            (graphics library)
```

Use `pip install pyvidplayer2[all]` to install all optional packages. Useful for developers running unit tests, but is
not required or recommended for regular users.

# Documentation

Refer to this [page](https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md) for detailed information.
To get started quickly, you can browse the many [code examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples).
If you prefer natural language, try asking [DeepWiki](https://deepwiki.com/anrayliu/pyvidplayer2). If you still have questions, 
open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues).


## Quickstart

Refer to the [examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples) folder for more basic examples.

### Pygame Integration

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
