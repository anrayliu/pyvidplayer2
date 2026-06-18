# pyvidplayer2

[![PyPI Version](https://img.shields.io/pypi/v/pyvidplayer2?logo=pypi&logoColor=white)](https://pypi.org/project/pyvidplayer2/)
[![PyPI Downloads](https://static.pepy.tech/badge/pyvidplayer2)](https://pepy.tech/projects/pyvidplayer2)
[![Status](https://img.shields.io/pypi/status/pyvidplayer2)](https://pypi.org/project/pyvidplayer2/)
![Coverage](https://img.shields.io/badge/Coverage-94%25-red)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fanrayliu%2Fpyvidplayer2%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anrayliu/pyvidplayer2)
[![Made with ❤️](https://img.shields.io/badge/Made_with-❤️-blue?style=round-square)](https://github.com/anrayliu/pyvidplayer2)

Comprehensive video playback library for Python.

This library is under active development. If you encounter a bug or a video that cannot be
played, please open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues).

<p align="center">
  <img src="demo.gif" />
</p>

## Features

- **Easy integration**: Add a video to an existing app with just 4 lines of code
- **Lightweight**: Almost every dependency is optional
- **Feature-rich**: Seamless loops, custom playback speed, reverse playback, parallel playback, and more
- **Full audio support**: Adjust audio track, output device, volume, and more
- **Full subtitle support**: Parse subtitles from files or embedded subtitle tracks
- **Play any format**: Supports almost every codec and container, VFR videos, even GIFs
- **YouTube integration**: Stream videos and subtitles directly from YouTube
- **Low-level control**: Frame-by-frame iteration and inspection
- **High compatibility**: Integrates with 7 graphics libraries (some features limited to Pygame)
- **Extra features**: Built-in video player GUI, post-processing effects, and webcam features

## Installation

```
pip install pyvidplayer2
```
In addition, FFmpeg and FFprobe must be downloaded and accessible via PATH.
Windows users can go to the [official website](https://www.ffmpeg.org/) to download FFmpeg (includes FFprobe).
Add the bin folder location to the PATH environment variable. There's plenty of tutorials online for this.
Linux and MacOS users can use their package manager of choice.

### Legacy Installations

Versions prior to v0.9.31 have a PyAudio dependency. To build the wheel for it, some system packages must be present.
Install them with your package manager before running `pip install pyvidplayer2`.

- Ubuntu/Debian: `sudo apt install python3-dev libjack-jackd2-dev portaudio19-dev`
- Fedora/RHEL: `sudo dnf install python3-devel portaudio-devel`
- MacOS: `brew install portaudio`

## Dependencies

```
numpy
FFmpeg and FFprobe (binaries, not Python packages)
```

Still requires one graphics library and one audio library of your choice.

### Optional Packages

```
opencv_python       (efficiency improvements and more features, comes installed)
pygame/pygame-ce    (graphics and audio library)
sounddevice         (better audio library, comes installed)
pysubs2             (for subtitles)
yt_dlp[default]     (for streaming Youtube videos)
decord              (for videos in bytes, best option)
imageio[pyav]       (for videos in bytes)
pyglet              (graphics library)
PySide6             (graphics library)
PyQt6               (graphics library)
tkinter             (graphics library, installed as a sys package or with Python installer, not pip)
raylib              (graphics library)
wxPython            (graphics library)
```

Use `pip install pyvidplayer2[all]` to install all packages required for running the unit tests.
Not required or recommended for regular users.

# Quickstart

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

## Documentation

To get started quickly, you can browse the many [code examples](https://github.com/anrayliu/pyvidplayer2/tree/main/examples).
For more detailed information, read the [documentation](https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md).
If you prefer natural language, try asking [DeepWiki](https://deepwiki.com/anrayliu/pyvidplayer2). If you still have questions, 
open an [issues page](https://github.com/anrayliu/pyvidplayer2/issues).

## Known Bugs

For a list of known bugs, refer to [this page](https://github.com/anrayliu/pyvidplayer2/issues/53).
If you see an issue not listed, please open a new issue.
