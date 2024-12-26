[![downloads](https://static.pepy.tech/badge/pyvidplayer2)](http://pepy.tech/project/pyvidplayer2)

# pyvidplayer2 (please report all bugs!)
Languages: English | [中文](https://github.com/anrayliu/pyvidplayer2/blob/main/README.cn.md)


Introducing pyvidplayer2, the successor to pyvidplayer. It's better in
pretty much every way, and finally allows an easy way to play videos in Python. 
Please note that this library is currently under development, so if you encounter a bug or a video that cannot be played, please open an issue at https://github.com/anrayliu/pyvidplayer2/issues.

All the features from the original library have been ported over, with the exception of `alt_resize()`. Since pyvidplayer2 has a completely revamped foundation, the unreliability of `set_size()` has been quashed, and a fallback function is now redundant.

# Features (see examples folder)
- Easy to implement (4 lines of code)
- Only essential dependencies are numpy, FFmpeg + FFprobe (cv2 is just nice to have)
- Fast and reliable
- Low CPU usage
- No audio/video sync issues
- Unlocked frame rate
- Can play a huge variety of video formats
- Play variable frame rate videos (VFR)
- Adjust playback speed
- Reverse playback
- Subtitle support (.srt, .ass, etc)
- Play multiple videos in parallel
- Add multiple subtitles to a video
- Built in GUI and queue system
- Support for Pygame, PygameCE, Pyglet, Tkinter, PySide6 and PyQT6
- Post process effects
- Webcam feed
- Stream videos from Youtube
- Grab subtitles from Youtube, including automatic generation and translation
- Play videos as byte objects
- Specify which audio devices to use
- Frame-by-frame iteration
- Choose audio different audio tracks

# Installation

## Windows
```
pip install pyvidplayer2
```
Note: FFMPEG (just the essentials is fine) must be installed and accessible via the system PATH. Here's an online article on how to do this (windows):
https://phoenixnap.com/kb/ffmpeg-windows.
FFPROBE may also be needed for certain features - this should come bundled with the FFMPEG download.

## Linux
Before running `pip install pyvidplayer2`, you must first install the required development packages.
- Ubuntu/Debian example: `sudo apt install build-essential python3-dev portaudio19-dev libjack-jackd2-dev`
  - The Python and PortAudio development packages prevent missing Python.h and missing portaudio.h errors, respectively.
  - Installing `libjack-jackd2-dev` manually prevents `portaudio19-dev` from downgrading to libjack0 and removing wine etc (<https://bugs.launchpad.net/ubuntu/+source/portaudio19/+bug/132002>).
  - In some circumstances, such as if you are using the kxstudio repo with Linux Mint, incompatible packages may be removed (See <https://github.com/anrayliu/pyvidplayer2/issues/36> for the latest updates on this issue):
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
FFMPEG and FFPROBE can easily be installed with homebrew.
```
brew install ffmpeg
```

# Dependencies

```
numpy
FFmpeg and FFprobe (not Python packages)
```

## Optional Packages

```
opencv_python   (efficiency improvements and more features, comes installed)
pygame          (graphics and audio library, comes installed)
PyAudio         (better audio library, comes installed)
pysubs2         (for subtitles, comes installed)
yt_dlp          (for streaming Youtube videos)
imageio         (for videos in bytes)
pyglet          (graphics library)
PySide6         (graphics library)
PyQt6           (graphics library)
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

# Known Bugs (as of v0.9.25)

- Youtube videos will sometimes freeze or stutter (rare)
- Video seeking is slow when reading from bytes
- Rotated videos when playing from bytes will appear in their original direction


# Documentation 

Documentation also available in repository as documentation.md.

# Video(path, chunk_size=10, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp="linear", use_pygame_audio=False, reverse=False, no_audio=False, speed=1, youtube=False, max_res=1080, as_bytes=False, audio_track=0, vfr=False, pref_lang="en", audio_index=None)

Main object used to play videos. Videos can be read from disk, memory or streamed from Youtube. The object uses FFMPEG to extract chunks of audio from videos and then feeds it into a Pyaudio stream. It uses OpenCV to display the appropriate video frames. Videos can only be played simultaneously if they're using Pyaudio (see `use_pygame_audio` below). Pygame or Pygame CE are the only graphics libraries to support subtitles. YTDLP is required to stream videos from Youtube. IMAGEIO and PyAV are required to play videos from memory. This particular object uses Pygame for graphics, but see bottom for other supported libraries. Actual class name is `VideoPygame`.

## Parameters
 - `path: str | bytes` - Path to video file. Supports almost all file types such as mkv, mp4, mov, avi, 3gp, etc. Can also provide the video in bytes (see `as_bytes` below). If streaming from Youtube (see `youtube` below), provide the URL here.
 - `chunk_size: float` - How much audio is extracted at a time, in seconds. Increasing this value will slow the initial loading of video, but is necessary to prevent stuttering. Recommended to keep over 60 if streaming from Youtube (see `youtube` below).
 - `max_threads: int` - Maximum number of chunks that can be extracted at any given time. Do not change if streaming from Youtube (see `youtube` below).
 - `max_chunks: int` - Maximum number of chunks allowed to be extracted and reserved. Do not change if streaming from Youtube (see `youtube` below).
 - `subs: pyvidplayer2.Subtitles` - Pass a `Subtitles` object here for the video to display subtitles.
 - `post_process: function(numpy.ndarray) -> numpy.ndarray` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place. Post processing functions should accept a NumpPy image (see `frame_data` below) and return the processed image.
 - `interp: str | int` - Interpolation technique used when resizing frames with OpenCV. Does nothing if OpenCv is not installed. Accepts `"nearest"`, `"linear"`, `"cubic"`, `"lanczos4"` and `"area"`. Nearest is the fastest technique but produces the worst results. Lanczos4 produces the best results but is so much more intensive that it's usually not worth it. Area is a technique that produces the best results when downscaling. This parameter can also accept OpenCV constants as in `cv2.INTER_LINEAR`.
 - `use_pygame_audio: bool` - Specifies whether to use Pyaudio or Pygame to play audio. Pyaudio is almost always the best option, so this is mostly obsolete. Using Pygame audio will not allow videos to be played in parallel. 
 - `reverse: bool` - Specifies whether to play the video in reverse. Warning: Doing so will load every video frame into memory, so videos longer than a few minutes can temporarily brick your computer. Subtitles are currently unaffected by reverse playback.
 - `no_audio: bool` - Specifies whether the given video has no audio tracks. Setting this to `True` can also be used to disable all existing audio tracks.
 - `speed: float | int` - Float from 0.5 to 10.0 that multiplies the playback speed. Note that if for example, speed=2, the video will play twice as fast. However, every single video frame will still be processed. Therefore, the frame rate of your program must be at least twice that of the video's frame rate to prevent dropped frames. So for example, for a 24 fps video, the video will have to be updated (see `draw` below) at least, but ideally more than 48 times a second to achieve true x2 speed.
 - `youtube: bool` - Specifies whether to stream a Youtube video. Path must be a valid Youtube video URL. The python packages yt_dlp and opencv-python are required for this feature. They can be installed through pip. Setting this to `True` will force `chunk_size` to be at least 60 and `max_threads` to be 1. Cannot play active livestreams.
 - `max_res: int` - Only used when streaming Youtube videos. Sets the highest possible resolution when choosing video quality. 4320p is the highest Youtube supports. Note that actual video quality is not guaranteed to match `max_res`.
 - `as_bytes: bool` - Specifies whether `path` is a video in byte form. The python packages imageio and av are required for this feature. It can be installed through pip.
 - `audio_track: int` - Selects which audio track to use. 0 will play the first, 1 will play the second, and so on.
 - `vfr: bool` - Used to play variable frame rate videos properly. If `False`, a constant frame rate will be assumed. If `True`, presentation timestamps will be extracted for each frame (see `timestamps` below). This still works for constant frame rate videos, but extracting the timestamps will mean a longer initial load.
 - `pref_lang: str` - Only used when streaming Youtube videos. Used to select a language track if video has multiple.
 - `audio_index: int` - Used to specify which audio output device to use. Can be specific to each video, and is automatically calculated if argument is not provided. To get a list of devices and their indices, use libraries like sounddevice (see audio_devices_demo.py in examples folder). Please use MME devices for Windows.

## Attributes
 - `path: str | bytes` - Same as given argument.
 - `name: str` - Name of file without the directory and extension. Will be an empty string if video is given in byte form (see `as_bytes` above).
 - `ext: str` - Type of video (mp4, mkv, mov, etc). Will be `"webm"` if streaming from Youtube (see `youtube` above). Will be an empty string if video is given in byte form (see `as_bytes` above).
 - `frame: int` - Current frame index. Starts from 0.
 - `frame_rate: float` - Float that indicates how many frames are in one second.
 - `max_fr: float` - Only used if `vfr = True`. Gives the maximum frame rate throughout the video.
 - `min_fr: float` - Only used if `vfr = True`. Gives the minimum frame rate throughout the video.
 - `avg_fr: float` - Only used if `vfr = True`. Gives the average frame rate of all the extracted presentation timestamps.
 - `timestamps: [float]` - List of presentation timestamps for each frame.
 - `frame_count: int` - How many total frames there are. May not be 100% accurate. For a more accurate (but slower) frame count,set `vfr = True` and use `len(video.timestamps)`.
 - `frame_delay: float` - Time between frames in order to maintain frame rate (in fractions of a second).
 - `duration: float` - Length of video in seconds.
 - `original_size: (int, int)` - Tuple containing the width and height of each original frame. Unaffected by resizing.
 - `current_size: (int, int)` - Tuple containing the width and height of each frame being rendered. Affected by resizing.
 - `aspect_ratio: float` - Width divided by height of original size.
 - `chunk_size: float` - Same as given argument. May change if `youtube` is `True` (see `youtube` above).
 - `max_chunks: int` - Same as given argument.
 - `max_threads: int` - Same as given argument. May change if `youtube` is `True` (see `youtube` above).
 - `frame_data: numpy.ndarray` - Current video frame as a NumPy `ndarray`.
 - `frame_surf: pygame.Surface` - Current video frame as a Pygame `Surface`.
 - `active: bool` - Whether the video is currently playing. This is unaffected by pausing and resuming.
 - `buffering: bool` - Whether the video is waiting for audio to extract.
 - `paused: bool`
 - `volume: float`
 - `muted: bool`
 - `speed: float | int` - Same as given argument.
 - `subs: pyvidplayer2.Subtitles` - Same as given argument.
 - `post_func: function(numpy.ndarray) -> numpy.ndarray` - Same as given argument. Can be changed with `set_post_func`.
 - `interp: int` - Same as given argument. Can be changed with `set_interp`. Will be converted to an integer if given a string. For example, if `"linear"` is given during initialization, this will be converted to cv2.INTER_LINEAR.
 - `use_pygame_audio: bool` - Same as given argument. May be automatically set to default sound backend.
 - `reverse: bool` - Same as given argument.
 - `no_audio: bool` - Same as given argument. May change if no audio is automatically detected.
 - `youtube: bool` - Same as given argument.
 - `max_res: int` - Same as given argument.
 - `as_bytes: bool` - Same as given argument. May change if bytes are automatically detected.
 - `audio_track: int` - Same as given argument.
 - `vfr: bool` - Same as given argument. 
 - `pref_lang: str` - Same as given argument.
 - `audio_index: int` - Same as given argument.
 - `subs_hidden: bool` - True if subs are currently disabled and False otherwise.
 
## Methods
 - `play() -> None` - Sets `active` to `True`.
 - `stop() -> None` - Resets video and sets `active` to `False`.
 - `resize(size: (int, int)) -> None`
 - `change_resolution(height: int) -> None` - Given a height, the video will scale it's dimensions while maintaining aspect ratio.
 - `close() -> None` - Releases resources. Always recommended to call when done.
 - `restart() -> None`
 - `get_speed() -> float | int`
 - `set_volume(volume: float) -> None` - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
 - `get_volume() -> float`
 - `get_paused() -> bool`
 - `toggle_pause() -> None` - Pauses if the video is playing, and resumes if the video is paused.
 - `pause() -> None`
 - `resume() -> None`
 - `set_audio_path(index: int)` - Sets the audio track used (see `audio_track` above).
 - `toggle_mute() -> None`
 - `mute() -> None`
 - `unmute() -> None`
 - `set_interp(interp: str | int) -> None` - Changes the interpolation technique that OpenCV uses. Works the same as the `interp` parameter (see `interp` above). Does nothing if OpenCV is not installed.
 - `set_post_func(func: function(numpy.ndarray) -> numpy.ndarray) -> None` - Changes the post processing function. Works the same as the `post_func` parameter (see `post_func` above). 
 - `get_pos(): float` - Returns the current position in seconds.
 - `seek(time: float | int, relative: bool = True) -> None` - Changes the current position in the video. If relative is `True`, the given time will be added or subtracted to the current time. Otherwise, the current position will be set to the given time exactly. Time must be given in seconds, and seeking will be accurate to one hundredth of a second. Note that 
 frames and audio within the video will not yet be updated after calling seek.
 - `seek_frame(index: int, relative: bool = False) -> None` - Same as `seek` but seeks to a specific frame instead of a time stamp. For example, index 0 will seek to the first frame, index 1 will seek to the second frame, and so on.
 - `update() -> bool` - Allows video to perform required operations. `draw` already calls this method, so it's usually not used. Returns `True` if a new frame is ready to be displayed.
 - `draw(surf: pygame.Surface, pos: (int, int), force_draw: bool = True) -> bool` - Draws the current video frame onto the given surface, at the given position. If `force_draw` is `True`, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces CPU usage but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn.
 - `preview(show_fps: bool = False, max_fps: int = 60) -> None` - Opens a window and plays the video. This method will hang until the video finishes. `max_fps` enforces how many times a second the video is updated. If `show_fps` is `True`, a counter will be displayed showing the actual number of new frames being rendered every second.
 - `show_subs() -> None` - Enables subtitles.
 - `hide_subs() -> None` - Disables subtitles.
 - `set_subs(subs: Subtitles | [Subtitles]) -> None` - Set the subtitles to use. Works the same as providing subtitles through the initialization parameter.

## Supported Graphics Libraries
 - Pygame or Pygame CE (`Video`) <- default and best supported
 - Tkinter (`VideoTkinter`)
 - Pyglet (`VideoPyglet`)
 - PySide6 (`VideoPySide`)
 - PyQT6 (`VideoPyQT`)

To use other libraries instead of Pygame, use their respective video object. Each preview method will use their respective graphics API to create a window and draw frames. See the examples folder for details. Note that `Subtitles`, `Webcam`, and `VideoPlayer` only work with Pygame installed. Preview methods for other graphics libraries also do not accept any arguments.

## As a Generator

Video objects can be iterated through as a generator, returning each subsequent frame. Frames will be given in reverse if video is reversed, and post processing and resizing will still take place. After iterating through frames, `play()` will resume the video from where the last frame left off. Returned frames will be in BGR format.
```
for frame in Video("example.mp4"):
    print(frame)
```

## In a Context Manager

Video objects can also be opened using context managers which will automatically call `close()` (see `close()` above) when out of use.
```
with Video("example.mp4") as vid:
    vid.preview()
```


# VideoPlayer(video, rect, interactable=False, loop=False, preview_thumbnails=0, font_size=10)

VideoPlayers are GUI containers for videos. They are useful for scaling a video to fit an area or looping videos. Only supported for Pygame.

## Parameters
 - `video: pyvidplayer2.VideoPygame` - Video object to play.
 - `rect: (int, int, int, int)` - An x, y, width, and height of the VideoPlayer. The top left corner will be the x, y coordinate.
 - `interactable: bool` - Enables the GUI.
 - `loop: bool` - Specifies whether the contained video will restart after it finishes. If the queue is not empty, the entire queue will loop, not just the current video.
 - `preview_thumbnails: int` - Number of preview thumbnails loaded and saved in memory. When seeking, a preview window will show the closest loaded frame. The higher this number is, the more frames are loaded, increasing the preview accuracy but also increasing initial load time and memory usage. Because of this, this value is defaulted to 0, which turns seek previewing off.
 - `font_size: int` - Sets font size for GUI elements.

## Attributes 
 - `video: pyvidplayer2.VideoPygame` - Same as given argument.
 - `frame_rect: (int, int, int, int)` - Same as given argument.
 - `vid_rect: (int, int, int, int)` - Location and dimensions (x, y, width, height) of the video fitted into `frame_rect` while maintaining aspect ratio. Black bars will appear in any unused space.
 - `interactable: bool` - Same as given argument.
 - `loop: bool` - Same as given argument.
 - `queue_: list[pyvidplayer2.VideoPygame | str]` - Videos to play after the current one finishes.
 - `preview_thumbnails: int` - Same as given argument.

## Methods
 - `zoom_to_fill() -> None` - Zooms in the video so that `frame_rect` is entirely filled in while maintaining aspect ratio.
 - `zoom_out() -> None` - Reverts `zoom_to_fill()`.
 - `toggle_zoom() -> None` - Switches between zoomed in and zoomed out.
 - `queue(input: pyvidplayer2.VideoPygame | str) -> None` - Accepts a path to a video or a Video object and adds it to the queue. Passing a path will not load the video until it becomes the active video. Passing a Video object will cause it to silently load its first audio chunk, so changing videos will be as seamless as possible.
 - `get_queue(): list[pyvidplayer2.VideoPygame]` - Returns list of queued video objects.
 - `resize(size: (int, int)) -> None` - Resizes the video player. The contained video will automatically readjust to fit the player.
 - `move(pos: (int, int), relative: bool = False) -> None` - Moves the VideoPlayer. If `relative` is `True`, the given coordinates will be added onto the current coordinates. Otherwise, the current coordinates will be set to the given coordinates.
 - `update(events: list[pygame.event.Event], show_ui: bool = None, fps: int = 0) -> bool` - Allows the VideoPlayer to make calculations. It must be given the returns of `pygame.event.get()`. The GUI automatically shows up when your mouse hovers over the video player, so setting `show_ui` to `False` can be used to override that. The `fps` parameter can enforce be used to enforce a frame rate to your app. This method also returns whether the UI was shown.
 - `draw(surface: pygame.Surface) -> None` - Draws the VideoPlayer onto the given Pygame surface.
 - `close() -> None` - Releases resources. Always recommended to call when done.
 - `skip() -> None` - Moves onto the next video in the queue.
 - `get_video() -> pyvidplayer2.VideoPygame` - Returns currently playing video.


# Subtitles(path, colour="white", highlight=(0, 0, 0, 128), font=pygame.font.SysFont("arial", 30), encoding="utf-8-sig", offset=50, delay=0, youtube=False, pref_lang="en")

Object used for handling subtitles. Only supported for Pygame.

## Parameters
 - `path: str` - Path to subtitle file. This can be any file pysubs2 can read including .srt, .ass, .vtt, and others. Can also be a youtube url if `youtube = True`.
 - `colour: str | (int, int, int)` - Colour of text as an RGB value or a string recognized by Pygame.
 - `highlight: str | (int, int, int, int)` - Background colour of text. Accepts RGBA, so it can be made completely transparent.
 - `font: pygame.font.Font | pygame.font.SysFont` - Pygame `Font` or `SysFont` object used to render surfaces. This includes the size of the text.
 - `encoding: str` - Encoding used to open subtitle files.
 - `offset: float` - The higher this number is, the closer the subtitle is to the top of the screen.
 - `delay: float` - Delays all subtitles by this many seconds.
 - `youtube: bool` - Set this to true and put a youtube video url into path to grab subtitles. 
 - `pref_lang: str` - Which language file to grab if `youtube = True`. If no subtitle file exists for this language, automatic captions are used, which are also automatically translated into the preferred language.

## Attributes
 - `path: str` - Same as given argument.
 - `encoding: str` - Same as given argument.
 - `start: float` - Starting timestamp of current subtitle.
 - `end: float` - Ending timestamp of current subtitle.
 - `text: str` - Current subtitle text.
 - `surf: pygame.Surface` - Current text in a Pygame `Surface`.
 - `colour: str | (int, int, int)` - Same as given argument.
 - `highlight: str | (int, int, int, int)` - Same as given argument.
 - `font: pygame.font.Font | pygame.font.SysFont` - Same as given argument.
 - `offset: float` - Same as given argument.
 - `delay: float` - Same as given argument.
 - `youtube: bool` - Same as given argument.
 - `pref_lang: str` - Same as given argument.

## Methods 
 - `set_font(font: pygame.font.Font | pygame.font.SysFont) -> None` - Same as `font` parameter (see `font` above).
 - `get_font() -> pygame.font.Font | pygame.font.SysFont`


# Webcam(post_process=PostProcessing.none, interp="linear", fps=30, cam_id=0)

Object used for displaying a webcam feed. Only supported for Pygame.

## Parameters
 - `post_process: function(numpy.ndarray) -> numpy.ndarray` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place. Post processing functions should accept a NumpPy image (see `frame_data` below) and return the processed image.
 - `interp: str | int` - Interpolation technique used by OpenCV when resizing frames. Does nothing if OpenCV is not installed. Accepts `"nearest"`, `"linear"`, `"cubic"`, `"lanczos4"` and `"area"`. Nearest is the fastest technique but produces the worst results. Lanczos4 produces the best results but is so much more intensive that it's usually not worth it. Area is a technique that produces the best results when downscaling. This parameter can also accept OpenCV constants as in `cv2.INTER_LINEAR`.
 - `fps: int` - Maximum number of frames captured from the webcam per second.
 - `cam_id: int` - Specifies which webcam to use if there are more than one. 0 means the first, 1 means the second, and so on.

## Attributes
 - `post_process: function(numpy.ndarray) -> numpy.ndarray` - Same as given argument.
 - `interp: int` - Same as given argument.
 - `fps: int` - Same as given argument.
 - `original_size: (int, int)` - Tuple containing the width and height of each frame captured. Unaffected by resizing.
 - `current_size: (int, int)` - Tuple containing the width and height of each frame being rendered. Affected by resizing.
 - `aspect_ratio: float` - Width divided by height of original size.
 - `active: bool` - Whether the webcam is currently playing.
 - `frame_data: numpy.ndarray` - Current video frame as a NumPy `ndarray`. Will be in BGR format.
 - `frame_surf: pygame.Surface` - Current video frame as a Pygame `Surface`.
 - `cam_id: int` - Same as given argument.

## Methods
 - `play() -> None`
 - `stop() -> None`
 - `resize(size: (int, int)) -> None`
 - `change_resolution(height: int) -> None` - Given a height, the video will scale its width while maintaining aspect ratio.
 - `set_interp(interp: str | int) -> None` - Changes the interpolation technique that OpenCV uses. Works the same as the `interp` parameter (see `interp` above). Does nothing if OpenCV is not installed.
  - `set_post_func(func: function(numpy.ndarray) -> numpy.ndarray) -> None` - Changes the post processing function. Works the same as the `post_func` parameter (see `post_func` above). 
 - `close() -> None` - Releases resources. Always recommended to call when done.
 - `get_pos() -> float` - Returns how long the webcam has been active. Is not reset if webcam is stopped.
 - `update() -> bool` - Allows webcam to perform required operations. `draw` already calls this method, so it's usually not used. Returns `True` if a new frame is ready to be displayed.
 - `draw(surf: pygame.Surface, pos: (int, int), force_draw: bool = True) -> bool` - Draws the current video frame onto the given surface, at the given position. If `force_draw` is `True`, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces CPU usage but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn.
 - `preview() -> None` - Opens a window and plays the webcam. This method will hang until the window is closed. Videos are played at whatever fps the webcam object is set to.


# PostProcessing

Used to apply various filters to video playback. Mostly for fun. Works across all graphics libraries. Requires OpenCV.

 - `none` - Default. Nothing happens.
 - `blur` - Slightly blurs frames.
 - `sharpen` - An okay-looking sharpen. Looks pretty bad for small resolutions.
 - `greyscale` - Removes colour from frame.
 - `noise` - Adds a static-like filter. Very resource intensive.
 - `letterbox` - Adds black bars above and below the frame to look more cinematic.
 - `cel_shading` - Thickens borders for a comic book style filter.

# Misc

```
print(pyvidplayer2.get_version_info())
```

Returns a dictionary with the version of pyvidplayer2, FFMPEG, and Pygame. Version can also be accessed directly
with `pyvidplayer2._version.__version__` or `pyvidplayer2.VERSION`.

When there are no suitable exceptions, `pyvidplayer2.Pyvidplayer2Error` may be raised.
