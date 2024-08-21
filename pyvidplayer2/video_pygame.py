import pygame
import numpy as np
from typing import Callable, Union, Tuple
from .video import Video
from .post_processing import PostProcessing
from .subtitles import Subtitles


class VideoPygame(Video):
    '''
    VideoPygame(path, chunk_size=10, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp="linear", use_pygame_audio=False, reverse=False, no_audio=False, speed=1, youtube=False, max_res=1080, as_bytes=False, audio_track=0)

        Main object used to play videos. Videos can be read from disk, memory or streamed from Youtube. The object uses FFMPEG to extract chunks of audio from videos and then feeds it into a Pyaudio stream. It uses OpenCV to display the appropriate video frames. Videos can only be played simultaneously if they're using Pyaudio (see use_pygame_audio below). YTDLP is required to stream videos from Youtube. Pysubs2 and Pygame is required to render subtitles. This object uses Pygame for graphics.

    Parameters
        path: str | bytes - Path to video file. Supports almost all file types such as mkv, mp4, mov, avi, 3gp, etc. Can also provide the video in bytes (see as_bytes below). If streaming from Youtube (see youtube below), provide the URL here.
        chunk_size: float - How much audio is extracted at a time, in seconds. Increasing this value will slow the initial loading of video, but is necessary to prevent stuttering. Recommended to keep over 60 if streaming from Youtube (see youtube below).
        max_threads: int - Maximum number of chunks that can be extracted at any given time. Do not change if streaming from Youtube (see youtube below).
        max_chunks: int - Maximum number of chunks allowed to be extracted and reserved. Do not change if streaming from Youtube (see youtube below).
        subs: pyvidplayer2.Subtitles - Pass a Subtitles object here for the video to display subtitles.
        post_process: function(numpy.ndarray) -> numpy.ndarray - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place. Post processing functions should accept a NumpPy image (see frame_data below) and return the processed image.
        interp: str | int - Interpolation technique used when resizing frames. Accepts "nearest", "linear", "cubic", "lanczos4" and "area". Nearest is the fastest technique but produces the worst results. Lanczos4 produces the best results but is so much more intensive that it's usually not worth it. Area is a technique that produces the best results when downscaling. This parameter can also accept OpenCV constants as in cv2.INTER_LINEAR.
        use_pygame_audio: bool - Specifies whether to use Pyaudio or Pygame to play audio. Pyaudio is almost always the best option, so this is mostly obsolete. Using Pygame audio will not allow videos to be played in parallel.
        reverse: bool - Specifies whether to play the video in reverse. Warning: Doing so will load every video frame into memory, so videos longer than a few minutes can temporarily brick your computer. Subtitles are currently unaffected by reverse playback.
        no_audio: bool - Specifies whether the given video has no audio tracks. Setting this to True can also be used to disable all existing audio tracks.
        speed: float | int - Float from 0.5 to 10.0 that multiplies the playback speed. Note that if for example, speed=2, the video will play twice as fast. However, every single video frame will still be processed. Therefore, the frame rate of your program must be at least twice that of the video's frame rate to prevent dropped frames. So for example, for a 24 fps video, the video will have to be updated (see draw below) at least, but ideally more than 48 times a second to achieve true x2 speed.
        youtube: bool - Specifies whether to stream a Youtube video. Path must be a valid Youtube video URL. The python package yt_dlp is required for this feature. It can be installed through pip. Setting this to True will force chunk_size to be at least 60, max_threads to be 1, and max_chunks to be 1. Cannot play active livestreams.
        max_res: int - Only used when streaming Youtube videos. Sets the highest possible resolution when choosing video quality. 4320p is the highest Youtube supports. Note that actual video quality is not guaranteed to match max_res.
        as_bytes: bool - Specifies whether path is a video in byte form.
        audio_track: int - Selects which audio track to use. 0 will play the first, 1 will play the second, and so on.

    Attributes
        path: str | bytes - Same as given argument.
        name: str - Name of file without the directory and extension. Will be None if video is given in byte form (see as_bytes above).
        ext: str - Type of video (mp4, mkv, mov, etc). Will be "webm" if streaming from Youtube (see youtube above). Will be None if video is given in byte form (see as_bytes above).
        frame: int - Current frame index. Starts from 0.
        frame_rate: float - Float that indicates how many frames are in one second.
        frame_count: int - How many total frames there are.
        frame_delay: float - Time between frames in order to maintain frame rate (in fractions of a second).
        duration: float - Length of video in seconds.
        original_size: (int, int) - Tuple containing the width and height of each original frame. Unaffected by resizing.
        current_size: (int, int) - Tuple containing the width and height of each frame being rendered. Affected by resizing.
        aspect_ratio: float - Width divided by height of original size.
        chunk_size: float - Same as given argument. May change if youtube is True (see youtube above).
        max_chunks: int - Same as given argument. May change if youtube is True (see youtube above).
        max_threads: int - Same as given argument. May change if youtube is True (see youtube above).
        frame_data: numpy.ndarray - Current video frame as a NumPy ndarray. Will be in BGR format.
        frame_surf: pygame.Surface - Current video frame as a Pygame Surface.
        active: bool - Whether the video is currently playing. This is unaffected by pausing and resuming.
        buffering: bool - Whether the video is waiting for audio to extract.
        paused: bool
        volume: float
        muted: bool
        speed: float | int - Same as given argument.
        subs: pyvidplayer2.Subtitles - Same as given argument.
        post_func: function(numpy.ndarray) -> numpy.ndarray - Same as given argument. Can be changed with set_post_func.
        interp: int - Same as given argument. Can be changed with set_interp. Will be converted to an integer if given a string. For example, if "linear" is given during initialization, this will be converted to cv2.INTER_LINEAR.
        use_pygame_audio: bool -  - Same as given argument.
        reverse: bool - Same as given argument.
        no_audio: bool - Same as given argument. May change if no audio is automatically detected.
        youtube: bool - Same as given argument.
        max_res: int - Same as given argument.
        as_bytes: bool - Same as given argument. May change if bytes are automatically detected.
        audio_track: int - Same as given argument.

    Methods:
        play() -> None - Sets active to True.
        stop() -> None - Resets video and sets active to False.
        resize(size: (int, int)) -> None
        change_resolution(height: int) -> None - Given a height, the video will scale it's dimensions while maintaining aspect ratio.
        close() -> None - Releases resources. Always recommended to call when done.
        restart() -> None
        get_speed() -> float | int
        set_volume(volume: float) -> None - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
        get_volume() -> float
        get_paused() -> bool
        toggle_pause() -> None - Pauses if the video is playing, and resumes if the video is paused.
        pause() -> None
        resume() -> None
        set_audio_track(index: int) - Sets the audio track used (see audio_track above).
        toggle_mute() -> None
        mute() -> None
        unmute() -> None
        set_interp(interp: str | int) -> None - Changes the interpolation technique. Works the same as the interp parameter (see interp above).
        set_post_func(func: function(numpy.ndarray) -> numpy.ndarray) -> None - Changes the post processing function. Works the same as the post_func parameter (see post_func above).
        get_pos(): floatReturns the current position in seconds.
        seek(time: float | int, relative: bool = True) -> None - Changes the current position in the video. If relative is True, the given time will be added or subtracted to the current time. Otherwise, the current position will be set to the given time exactly. Time must be given in seconds, and seeking will be accurate to one hundredth of a second. Note that
        frames and audio within the video will not yet be updated after calling seek.
        seek_frame(index: int, relative: bool = False) -> None - Same as seek but seeks to a specific frame instead of a time stamp. For example, index 0 will seek to the first frame, index 1 will seek to the second frame, and so on.
        draw(surf: pygame.Surface, pos: (int, int), force_draw: bool = True) -> bool - Draws the current video frame onto the given surface, at the given position. If force_draw is True, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces CPU usage but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn.
        preview(show_fps: bool = False, max_fps: int = 60) -> None - Opens a window and plays the video. This method will hang until the video finishes. max_fps enforces how many times a second the video is updated. If show_fps is True, a counter will be displayed showing the actual number of new frames being rendered every second.
    '''
    
    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1, subs: Subtitles = None, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False, no_audio: bool = False, speed: float = 1, youtube: bool = False, max_res: int = 1080, 
                 as_bytes: bool = False, audio_track: int = 0) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track)

    def __str__(self) -> str:
        return f"<VideoPygame(path={self.path})>"

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf, pos):
        surf.blit(self.frame_surf, pos)

    def draw(self, surf: pygame.Surface, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        return Video.draw(self, surf, pos, force_draw)
    
    def preview(self, show_fps: bool = False, max_fps: int = 60) -> None:
        win = pygame.display.set_mode(self.current_size)
        clock = pygame.time.Clock()
        pygame.display.set_caption(f"pygame - {self.name}")
        self.play()
        timer = 0
        fps = 0
        frames = 0
        font = pygame.font.SysFont("arial", 30)
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
            dt = clock.tick(max_fps)
            if show_fps:
                timer += dt 
                if timer >= 1000:
                    fps = frames 
                    timer = 0
                    frames = 0
            if self.draw(win, (0, 0), force_draw=False):
                if show_fps:
                    frames += 1
                    surf = font.render(str(fps), True, "white")
                    pygame.draw.rect(win, "black", surf.get_rect(topleft=(0, 0)))
                    win.blit(surf, (0, 0))
                pygame.display.update()
        pygame.display.quit()
        self.close()
