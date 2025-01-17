# Video(path, chunk_size=10, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp="linear", use_pygame_audio=False, reverse=False, no_audio=False, speed=1, youtube=False, max_res=720, as_bytes=False, audio_track=0, vfr=False, pref_lang="en", audio_index=None, reader=pyvidplayer2.READER_AUTO)

Main object used to play videos. Videos can be read from disk, memory or streamed from Youtube. The object uses FFMPEG to extract chunks of audio from videos and then feeds it into a Pyaudio stream. It uses OpenCV to display the appropriate video frames. Videos can only be played simultaneously if they're using Pyaudio (see `use_pygame_audio` below). Pygame or Pygame CE are the only graphics libraries to support subtitles. YTDLP is required to stream videos from Youtube. Decord is required to play videos from memory. This particular object uses Pygame for graphics, but see bottom for other supported libraries. Actual class name is `VideoPygame`.

## Parameters
 - `path: str | bytes` - Path to video file. Supports almost all file types such as mkv, mp4, mov, avi, 3gp, etc. Can also provide the video in bytes (see `as_bytes` below). If streaming from Youtube (see `youtube` below), provide the URL here.
 - `chunk_size: float` - How much audio is extracted at a time, in seconds. Increasing this value will slow the initial loading of video, but is necessary to prevent stuttering. Recommended to keep over 60 if streaming from Youtube (see `youtube` below).
 - `max_threads: int` - Maximum number of chunks that can be extracted at any given time. Do not change if streaming from Youtube (see `youtube` below).
 - `max_chunks: int` - Maximum number of chunks allowed to be extracted and reserved. Do not change if streaming from Youtube (see `youtube` below).
 - `subs: pyvidplayer2.Subtitles` - Pass a `Subtitles` object here for the video to display subtitles.
 - `post_process: function(numpy.ndarray) -> numpy.ndarray` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place. Post processing functions should accept a NumpPy image (see `frame_data` below) and return the processed image.
 - `interp: str | int` - Interpolation technique used when resizing frames. Accepts `"nearest"`, `"linear"`, `"cubic"`, `"lanczos4"` and `"area"`. Nearest is the fastest technique but produces the worst results. Lanczos4 produces the best results but is so much more intensive that it's usually not worth it. Area is a technique that produces the best results when downscaling. This parameter can also accept OpenCV constants as in `cv2.INTER_LINEAR`. Resizing will use opencv when available but can fall back on ffmpeg if needed.
 - `use_pygame_audio: bool` - Specifies whether to use Pyaudio or Pygame to play audio. Pyaudio is almost always the best option, so this is mostly obsolete. Using Pygame audio will not allow videos to be played in parallel. 
 - `reverse: bool` - Specifies whether to play the video in reverse. Warning: Doing so will load every video frame into memory, so videos longer than a few minutes can temporarily brick your computer. Subtitles are currently unaffected by reverse playback.
 - `no_audio: bool` - Specifies whether the given video has no audio tracks. Setting this to `True` can also be used to disable all existing audio tracks.
 - `speed: float | int` - Float from 0.5 to 10.0 that multiplies the playback speed. Note that if for example, speed=2, the video will play twice as fast. However, every single video frame will still be processed. Therefore, the frame rate of your program must be at least twice that of the video's frame rate to prevent dropped frames. So for example, for a 24 fps video, the video will have to be updated (see `draw` below) at least, but ideally more than 48 times a second to achieve true x2 speed.
 - `youtube: bool` - Specifies whether to stream a Youtube video. Path must be a valid Youtube video URL. The python packages yt_dlp and opencv-python are required for this feature. They can be installed through pip. Setting this to `True` will force `chunk_size` to be at least 60 and `max_threads` to be 1. Cannot play active livestreams.
 - `max_res: int` - Only used when streaming Youtube videos. Sets the highest possible resolution when choosing video quality. 4320p is the highest Youtube supports. Note that actual video quality is not guaranteed to match `max_res`.
 - `as_bytes: bool` - Specifies whether `path` is a video in byte form. The python package decord is required for this feature. It can be installed through pip.
 - `audio_track: int` - Selects which audio track to use. 0 will play the first, 1 will play the second, and so on.
 - `vfr: bool` - Used to play variable frame rate videos properly. If `False`, a constant frame rate will be assumed. If `True`, presentation timestamps will be extracted for each frame (see `timestamps` below). This still works for constant frame rate videos, but extracting the timestamps will mean a longer initial load.
 - `pref_lang: str` - Only used when streaming Youtube videos. Used to select a language track if video has multiple.
 - `audio_index: int` - Used to specify which audio output device to use if using PyAudio. Can be specific to each video, and is automatically calculated if argument is not provided. To get a list of devices and their indices, use libraries like sounddevice (see audio_devices_demo.py in examples folder). Use the MME host APIs. If using Pygame instead of PyAudio, setting output device can be done in the mixer init settings, independent of pyvidplayer2.
 - `reader: int` - Specifies which video reading backend to use. Can be pyvidplayer2.READER_AUTO (choose best backend automatically), pyvidplayer2.READER_OPENCV, pyvidplayer2.READER_DECORD, pyvidplayer2.READER_IMAGEIO, and pyvidplayer2.READER_FFMPEG. Note that their respective packages must be installed to use. Also, the colour format varies between readers. READER_OPENCV and READER_FFMPEG use BGR while READER_IMAGEIO and READER_DECORD use RGB. (see `colour_format` below).

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
 - `frame_count: int` - How many total frames there are. May not be exactly accurate. For a more accurate (but slower) frame count, use `_get_real_frame_count()`.
 - `frame_delay: float` - Time between frames in order to maintain frame rate (in fractions of a second).
 - `duration: float` - Length of video in seconds.
 - `original_size: (int, int)` - Tuple containing the width and height of each original frame. Unaffected by resizing.
 - `current_size: (int, int)` - Tuple containing the width and height of each frame being rendered. Affected by resizing.
 - `aspect_ratio: float` - Width divided by height of original size.
 - `chunk_size: float` - Same as given argument. May change if `youtube` is `True` (see `youtube` above).
 - `max_chunks: int` - Same as given argument.
 - `max_threads: int` - Same as given argument. May change if `youtube` is `True` (see `youtube` above).
 - `frame_data: numpy.ndarray` - Current video frame as a NumPy `ndarray`. May be in a variety of colour formats (see `colour_format` below).
 - `frame_surf: pygame.Surface` - Current video frame as a Pygame `Surface`. Will be rendered in RGB.
 - `active: bool` - Whether the video is currently playing. This is unaffected by pausing and resuming.
 - `buffering: bool` - Whether the video is waiting for audio to extract.
 - `paused: bool`
 - `volume: float`
 - `muted: bool`
 - `speed: float | int` - Same as given argument.
 - `subs: pyvidplayer2.Subtitles` - Same as given argument.
 - `post_func: callable(numpy.ndarray) -> numpy.ndarray` - Same as given argument. Can be changed with `set_post_func`.
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
 - `closed: bool` - True after `close()` is called.
 - `colour_format: str` - Whatever colour format the current backend is reading in. OpenCV and FFmpeg use BGR, while Decord and ImageIO use RGB.
 
## Methods
 - `play() -> None` - Sets `active` to `True`.
 - `stop() -> None` - Resets video and sets `active` to `False`.
 - `resize(size: (int, int)) -> None`
 - `change_resolution(height: int) -> None` - Given a height, the video will scale it's dimensions while maintaining aspect ratio. Will scale width to an even number.
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
 - `set_post_func(func: callable(numpy.ndarray) -> numpy.ndarray) -> None` - Changes the post processing function. Works the same as the `post_func` parameter (see `post_func` above). 
 - `get_pos(): float` - Returns the current position in seconds.
 - `seek(time: float | int, relative: bool = True) -> None` - Changes the current position in the video. If relative is `True`, the given time will be added or subtracted to the current time. Otherwise, the current position will be set to the given time exactly. Time must be given in seconds, with no precision limit. Note that 
 frames and audio within the video will not yet be updated after calling seek. `update()` or `draw` must be called for internal processing to start. If the given value is larger than the video duration, the video will be seeked to the last frame. Calling `next(video)` will read the last frame.
 - `seek_frame(index: int, relative: bool = False) -> None` - Same as `seek` but seeks to a specific frame instead of a time stamp. For example, index 0 will seek to the first frame, index 1 will seek to the second frame, and so on. If the given index is larger than the total frames, the video will be seeked to the last frame.
 - `update() -> bool` - Allows video to perform required operations. `draw` already calls this method, so it's usually not used. Returns `True` if a new frame is ready to be displayed.
 - `draw(surf: pygame.Surface, pos: (int, int), force_draw: bool = True) -> bool` - Draws the current video frame onto the given surface, at the given position. If `force_draw` is `True`, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces CPU usage but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn.
 - `preview(show_fps: bool = False, max_fps: int = 60) -> None` - Opens a window and plays the video. This method will hang until the video finishes. `max_fps` enforces how many times a second the video is updated. If `show_fps` is `True`, a counter will be displayed showing the actual number of new frames being rendered every second.
 - `show_subs() -> None` - Enables subtitles.
 - `hide_subs() -> None` - Disables subtitles.
 - `set_subs(subs: Subtitles | [Subtitles]) -> None` - Set the subtitles to use. Works the same as providing subtitles through the initialization parameter.
 - `probe() -> None` - Uses FFprobe to find information about the video. When using cv2 to read videos, information such as frame count or frame rate are read through the file headers, which is sometimes incorrect. For more accuracy, call this method to start a probe and update the video information.

## Supported Graphics Libraries
 - Pygame or Pygame CE (`Video`) <- default and best supported
 - Tkinter (`VideoTkinter`)
 - Pyglet (`VideoPyglet`)
 - PySide6 (`VideoPySide`)
 - PyQT6 (`VideoPyQT`)
 - RayLib (`VideoRayLib`)

To use other libraries instead of Pygame, use their respective video object. Each preview method will use their respective graphics API to create a window and draw frames. See the examples folder for details. Note that `Subtitles`, `Webcam`, and `VideoPlayer` only work with Pygame installed. Preview methods for other graphics libraries also do not accept any arguments.

## As a Generator

Video objects can be iterated through as a generator, returning each subsequent frame. Frames will be given in reverse if video is reversed, and post processing and resizing will still take place. Subtitles will not be rendered. After iterating through frames, `play()` will resume the video from where the last frame left off. Returned frames will be in BGR format.
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
 - `closed: bool` - True after `close()` is called.

## Methods
 - `zoom_to_fill() -> None` - Zooms in the video so that `frame_rect` is entirely filled in while maintaining aspect ratio.
 - `zoom_out() -> None` - Reverts `zoom_to_fill()`.
 - `toggle_zoom() -> None` - Switches between zoomed in and zoomed out.
 - `queue(input: pyvidplayer2.VideoPygame | str) -> None` - Accepts a path to a video or a Video object and adds it to the queue. Passing a path will not load the video until it becomes the active video. Passing a Video object will cause it to silently load its first audio chunk, so changing videos will be as seamless as possible.
 - `get_queue(): list[pyvidplayer2.VideoPygame]` - Returns list of queued video objects.
 - `resize(size: (int, int)) -> None` - Resizes the video player. The contained video will automatically re-adjust to fit the player.
 - `move(pos: (int, int), relative: bool = False) -> None` - Moves the VideoPlayer. If `relative` is `True`, the given coordinates will be added onto the current coordinates. Otherwise, the current coordinates will be set to the given coordinates.
 - `update(events: list[pygame.event.Event], show_ui: bool = None, fps: int = 0) -> bool` - Allows the VideoPlayer to make calculations. It must be given the returns of `pygame.event.get()`. The GUI automatically shows up when your mouse hovers over the video player, so setting `show_ui` to `False` can be used to override that. The `fps` parameter can enforce be used to enforce a frame rate to your app. This method also returns whether the UI was shown.
 - `draw(surface: pygame.Surface) -> None` - Draws the VideoPlayer onto the given Pygame surface.
 - `close() -> None` - Releases resources. Always recommended to call when done.
 - `skip() -> None` - Moves onto the next video in the queue.
 - `get_video() -> pyvidplayer2.VideoPygame` - Returns currently playing video.
 - `preview(max_fps: int = 60)` - Similar to `Video.preview()`. Gives a quick and easy demo of the class.

# Subtitles(path, colour="white", highlight=(0, 0, 0, 128), font=None, encoding="utf-8", offset=50, delay=0, youtube=False, pref_lang="en", track_index=None)

Object used for handling subtitles. Only supported for Pygame.

## Parameters
 - `path: str` - Path to subtitle file. This can be any file pysubs2 can read including .srt, .ass, .vtt, and others. Can also be a youtube url if `youtube = True`. Can also be a video that contains subtitle tracks.
 - `colour: str | (int, int, int)` - Colour of text as an RGB value or a string recognized by Pygame.
 - `highlight: str | (int, int, int, int)` - Background colour of text. Accepts RGBA, so it can be made completely transparent.
 - `font: pygame.font.Font | pygame.font.SysFont` - Pygame `Font` or `SysFont` object used to render surfaces. This includes the size of the text.
 - `encoding: str` - Encoding used to open subtitle files.
 - `offset: float` - The higher this number is, the closer the subtitle is to the top of the screen.
 - `delay: float` - Delays all subtitles by this many seconds.
 - `youtube: bool` - Set this to true and put a youtube video url into path to grab subtitles. 
 - `pref_lang: str` - Which language file to grab if `youtube = True`. If no subtitle file exists for this language, automatic captions are used, which are also automatically translated into the preferred language. However, it's important to use the correct language code set by Google, otherwise the subtitles will not be found.
For example, usually setting `en` will get English subtitles. However, the video might be in `en-US` instead, so this is an important differentiation. Confirm which one your video has in Youtube first.
 - `track_index: int` - If path is given as a video with subtitle tracks, use this to specify which subtitle to load. 0 selects the first, 1 selects the second, etfc.

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
 - `buffer: str` - Entire subtitle file loaded into memory if downloaded.
 - `track_index: int` - Same as given argument.

## Methods 
 - `set_font(font: pygame.font.Font | pygame.font.SysFont) -> None` - Same as `font` parameter (see `font` above).
 - `get_font() -> pygame.font.Font | pygame.font.SysFont`


# Webcam(post_process=PostProcessing.none, interp="linear", fps=30, cam_id=0, capture_size=(0, 0))

Object used for displaying a webcam feed. Only supported for Pygame.

## Parameters
 - `post_process: callable(numpy.ndarray) -> numpy.ndarray` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place. Post processing functions should accept a NumpPy image (see `frame_data` below) and return the processed image.
 - `interp: str | int` - Interpolation technique used by OpenCV when resizing frames. Accepts `"nearest"`, `"linear"`, `"cubic"`, `"lanczos4"` and `"area"`. Nearest is the fastest technique but produces the worst results. Lanczos4 produces the best results but is so much more intensive that it's usually not worth it. Area is a technique that produces the best results when downscaling. This parameter can also accept OpenCV constants as in `cv2.INTER_LINEAR`. Resizing will use opencv when available but can fall back on ffmpeg if needed.
 - `fps: int` - Maximum number of frames captured from the webcam per second.
 - `cam_id: int` - Specifies which webcam to use if there are more than one. 0 means the first, 1 means the second, and so on.
 - `capture_size: int` - Specifies the webcam resolution. If nothing is set, a default is used.
 - 
## Attributes
 - `post_process: callable(numpy.ndarray) -> numpy.ndarray` - Same as given argument.
 - `interp: int` - Same as given argument.
 - `fps: int` - Same as given argument.
 - `original_size: (int, int)` - Size of raw frames captured by the webcam. Can be set with `resize_capture`.
 - `current_size: (int, int)` - Size of frames after resampling. Can be set with `resize`.
 - `aspect_ratio: float` - Width divided by height of original size.
 - `active: bool` - Whether the webcam is currently playing.
 - `frame_data: numpy.ndarray` - Current video frame as a NumPy `ndarray`. Will be in BGR format.
 - `frame_surf: pygame.Surface` - Current video frame as a Pygame `Surface`.
 - `cam_id: int` - Same as given argument.
 - `closed: bool` - True after `close()` is called.

## Methods
 - `play() -> None`
 - `stop() -> None`
 - `resize(size: (int, int)) -> None` - Simply sets dimensions that captured frames will be resized to.
 - `resize_capture(size: (int, int)) -> bool` -  Changes the resolution at which frames are captured from the webcam. Returns `True` if a resolution was found that matched the given size exactly. Otherwise, `False` will be returned and the closest matching resolution will be used.
 - `change_resolution(height: int) -> None` - Given a height, the video will scale its width while maintaining aspect ratio. Will scale width to an even number.
 - `set_interp(interp: str | int) -> None` - Changes the interpolation technique that OpenCV uses. Works the same as the `interp` parameter (see `interp` above). Does nothing if OpenCV is not installed.
  - `set_post_func(func: callable(numpy.ndarray) -> numpy.ndarray) -> None` - Changes the post processing function. Works the same as the `post_func` parameter (see `post_func` above). 
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
 - `fliplr` - Flips the video across y axis.
 - `flipup` - Flips the video across x axis.

# Errors 

- `Pyvidplayer2Error` - Base error for pyvidplayer2 related exceptions.
- `AudioDeviceError(Pyvidplayer2Error)` - Thrown for exceptions related to PyAudio output devices.
- `SubtitleError(Pyvidplayer2Error)` - Thrown for exceptions related to subtitles.
- `VideoStreamError(Pyvidplayer2Error)` - Thrown for exceptions related to general video probing and playback.
- `FFmpegNotFoundError(Pyvidplayer2Error)` - Thrown when FFmpeg is missing.
- `OpenCVError(Pyvidplayer2Error)` - Thrown for exceptions related to OpenCV processes.
- `YTDLPError(Pyvidplayer2Error)` - Thrown for exceptions related to YTDLP processes.
- `WebcamNotFoundError(Pyvidplayer2Error)` - Thrown when there are no webcams to activate.

# Misc

```
print(pyvidplayer2.get_version_info())
```

Returns a dictionary with the version of pyvidplayer2, FFMPEG, and Pygame. Version can also be accessed directly
with `pyvidplayer2.__version__` or `pyvidplayer2.VERSION`.
