import subprocess
import os
import json
from abc import abstractmethod

import numpy as np
from typing import Union, Callable, Tuple
from threading import Thread
from .ffmpeg_reader import FFMPEGReader
from .error import *
from . import FFMPEG_LOGLVL

try:
    import cv2
except ImportError:
    CV = 0
else:
    CV = 1
    from .cv_reader import CVReader

try:
    import pyaudio
except ImportError:
    PYAUDIO = 0
else:
    PYAUDIO = 1
    from .pyaudio_handler import PyaudioHandler

try:
    import pygame
except ImportError:
    PYGAME = 0
else:
    PYGAME = 1
    from .mixer_handler import MixerHandler

try:
    import yt_dlp
except ImportError:
    YTDLP = 0
else:
    YTDLP = 1

try:
    import imageio.v3
except ImportError:
    IIO = 0
else:
    IIO = 1
    from .imageio_reader import IIOReader

try:
    import decord
except ImportError:
    DECORD = 0
else:
    DECORD = 1
    from .decord_reader import DecordReader

try:
    from .subtitles import Subtitles
except ImportError:
    SUBS = 0
else:
    SUBS = 1


# for specifying different reader backends
READER_AUTO = 0
READER_FFMPEG = 1
READER_OPENCV = 2
READER_IMAGEIO = 3
READER_DECORD = 4


class Video:
    def __init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp, use_pygame_audio, reverse, no_audio, speed, 
                 youtube, max_res, as_bytes, audio_track, vfr, pref_lang, audio_index, reader):
        
        self._audio_path = path     # used for audio only when streaming
        self.path = path

        self.name = "" 
        self.ext = ""

        as_bytes = as_bytes or isinstance(path, bytes)
        #youtube = youtube or self._test_youtube()

        self.pref_lang = pref_lang

        # determines correct backend here
        reader = self._get_best_reader(youtube, as_bytes, reader)
        if youtube:
            if YTDLP:
                # sets path and audio path for cv2 and ffmpeg
                # also sets name and ext
                self._set_stream_url(path, max_res)
                self._vid = reader(self.path)
            else:
                raise ModuleNotFoundError("Unable to stream video because YTDLP is not installed. YTDLP can be installed via pip.")

            # having less than 60 hurts performance
            if chunk_size < 60:
                chunk_size = 60
            if max_threads > 1:
                max_threads = 1

        elif as_bytes:
            self._vid = reader(self.path)
            self._audio_path = "-"  # read from pipe

        else:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"[Errno 2] No such file or directory: '{self.path}'")

            self._vid = reader(self.path)
            self.name, self.ext = os.path.splitext(os.path.basename(self.path))

        if not self._vid.isOpened() and CV:
            raise OpenCVError("Failed to open file.")

        self.colour_format = self._vid._colour_format

        # file information

        self.frame_count = self._vid.frame_count
        self.frame_rate = self._vid.frame_rate
        self.frame_delay = 1 / self.frame_rate
        self.duration = self._vid.duration
        self.original_size = self._vid.original_size
        self.current_size = self.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]
        self.audio_channels = 0

        self.chunk_size = 0 if chunk_size < 0 else chunk_size
        self.max_chunks = max_chunks
        self.max_threads = max_threads

        self._chunks = []
        self._threads = []
        self._starting_time = 0
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._buffer_first_chunk = False
        self._buffered_chunk = None
        self._stop_loading = False
        self._processes = []
        self.frame = 0

        self.frame_data = None
        self.frame_surf = None

        self.active = False
        self.buffering = False
        self.paused = False
        self.muted = False
        self.subs_hidden = False
        self.closed = False

        self.subs = self._filter_subs(subs)

        self.post_func = post_process
        self.interp = None
        self.use_pygame_audio = use_pygame_audio# or (PYGAME and not PYAUDIO)
        self.youtube = youtube
        self.max_res = max_res
        self.as_bytes = as_bytes
        self.audio_track = audio_track
        self.vfr = vfr #or self._test_vfr()
        self.audio_index = audio_index

        if self.use_pygame_audio:
            if PYGAME:
                self._audio = MixerHandler()
            else:
                raise ModuleNotFoundError("Unable to use Pygame audio because Pygame is not installed. Pygame can be installed via pip.")
        else:
            if PYAUDIO:
                self._audio = PyaudioHandler()
                if self.audio_index is not None:
                    self._audio._set_device_index(self.audio_index)
            else:
                raise ModuleNotFoundError("Unable to use PyAudio audio because PyAudio is not installed. PyAudio can be installed via pip.")
            
        self.speed = float(max(0.25, min(10, speed)))
        self.reverse = reverse
        self.no_audio = no_audio or self._test_no_audio()

        self._missing_ffmpeg = False  # for throwing errors
        self._generated_frame = False  # for when used as a generator
        self._preloaded = False
        self._update_time = 0.0 # for testing

        self.timestamps = []
        self.min_fr = self.max_fr = self.avg_fr = self.frame_rate
        if self.vfr:
            self.timestamps = self._get_all_pts()
            self.min_fr, self.max_fr, self.avg_fr = self._get_vfrs(self.timestamps)

        self._preloaded_frames = []
        if self.reverse:
            self._preload_frames()

        self.set_interp(interp)

        if not self.no_audio:
            self.set_audio_track(self.audio_track)

        self.play()

    def __len__(self):
        return self.frame_count

    def __str__(self):
        return f"<{type(self).__name__}(path={self.path if not (self.as_bytes or self.youtube) else ''})>"

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def __iter__(self):
        self.stop()
        return self

    def __next__(self) -> np.ndarray:
        self._generated_frame = True
        data = None

        if self.reverse:
            try:
                data = self._preloaded_frames[self.frame_count - self.frame - 1]
            except IndexError:
                pass
        else:
            data = self._vid.read()[1]

        if data is not None:
            self.frame += 1
            if self.original_size != self.current_size:
                data = self._resize_frame(data, self.current_size, self.interp, not CV)
            data = self.post_func(data)

            return data
        else:
            raise StopIteration("No more frames to read.")

    def _get_best_reader(self, youtube, as_bytes, reader):
        if youtube:
            if reader == READER_AUTO or reader == READER_OPENCV:
                if CV:
                    return CVReader
                elif reader != READER_AUTO:
                    ModuleNotFoundError(
                        "Unable to stream video because OpenCV is not installed. OpenCV can be installed via pip.")
            raise ValueError("Only READER_OPENCV is supported for Youtube videos.")
        elif as_bytes:
            if reader == READER_AUTO or reader == READER_DECORD:
                if DECORD:
                    return DecordReader
                elif reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "Unable to read video from memory because decord is not installed. Decord can be installed via pip.")
            if reader == READER_AUTO or reader == READER_IMAGEIO:
                if IIO:
                    return IIOReader
                elif reader != READER_AUTO:
                    raise ModuleNotFoundError("Unable to read video from memory because IMAGEIO is not installed. IMAGEIO can be installed via pip.")
            raise ValueError("Only READER_DECORD and READER_IMAGEIO is supported for reading from memory.")
        else:
            if reader == READER_AUTO or reader == READER_OPENCV:
                if CV:
                    return CVReader
                elif reader != READER_AUTO:
                    raise ModuleNotFoundError("OpenCV is not installed. OpenCV can be installed through pip.")
            if reader == READER_AUTO or reader == READER_DECORD:
                if DECORD:
                    return DecordReader
                elif reader != READER_AUTO:
                    raise ModuleNotFoundError("Decord is not installed. Decord can be installed through pip.")
            if reader == READER_AUTO or reader == READER_FFMPEG:
                return FFMPEGReader
            if reader == READER_IMAGEIO:
                if IIO:
                    return IIOReader
                raise ModuleNotFoundError("ImageIO is not installed. ImageIO can be installed through pip.")
            raise ValueError("Could not identify backend.")

    def _filter_subs(self, subs):
        if SUBS and isinstance(subs, Subtitles):
            return [subs]
        else:
            return [] if subs is None else subs
    
    def _get_vfrs(self, pts):
        # calculates differences in frametime, except the first and last frames are ignored because
        # they can be anomalous
        difs = [pts[i + 1] - pts[i] for i in range(1, len(pts) - 2)]
        if not difs:
            return 0, 0, 0

        min_fr = 1 / max(difs)
        max_fr = 1 / min(difs)
        avg_fr = len(difs) / sum(difs)

        return min_fr, max_fr, avg_fr

    def _get_all_pts(self):
        try:
            command = [
                "ffprobe",
                "-i", "-" if self.as_bytes else self.path,
                "-select_streams", "v:0",
                "-show_entries", "packet=pts_time",
                "-loglevel", FFMPEG_LOGLVL,
                "-print_format", "json"
            ]

            p = subprocess.Popen(command, stdin=subprocess.PIPE if self.as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FFmpegNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate(input=self.path if self.as_bytes else None)[0])

        pts = sorted([float(dict_["pts_time"]) for dict_ in info["packets"]])
        if pts:
            offset = pts[0]
            pts = [t - offset for t in pts]

        return pts

    # mainly for testing purposes
    def _force_ffmpeg_reader(self):
        if not isinstance(self._vid, FFMPEGReader):
            new_reader = FFMPEGReader(self.path, False)
            new_reader.frame_count = self._vid.frame_count
            new_reader.frame_rate = self._vid.frame_rate
            new_reader.original_size = self._vid.original_size
            new_reader.duration = self._vid.duration
            new_reader.frame = self._vid.frame
            new_reader.seek(self._vid.frame)
            self.colour_format = new_reader._colour_format
            self._vid.release()
            self._vid = new_reader

    def _set_stream_url(self, path, max_res):
        config = {"quiet": True,
                  "noplaylist": True,
                  # unfortunately must grab the worst audio because ffmpeg seeking is too slow for high quality audio
                  "format": f"bestvideo[height<={max_res}]+worstaudio[language={self.pref_lang}]/bestvideo[height<={max_res}]+worstaudio/best[height<={max_res}]"}

        with yt_dlp.YoutubeDL(config) as ydl:
            try:
                info = ydl.extract_info(path, download=False)
                formats = info.get("requested_formats", None)
                if formats is None:
                    raise YTDLPError("No streaming links found.")
            except YTDLPError:
                raise
            except Exception as e: # something went wrong with yt_dlp
                if "Requested format is not available" in str(e):
                    raise YTDLPError("Could not find requested resolution.")
                raise YTDLPError("yt-dlp could not open video. Please ensure the URL is a valid Youtube video.")
            else:
                self.path = formats[0]["url"]
                self._audio_path = formats[1]["url"]
                self.name = info.get("title", "")
                self.ext = ".webm"

    def _preload_frames(self):
        self._preloaded = True

        self._preloaded_frames.clear()

        self._vid.seek(0)

        has_frame = True
        while has_frame:
            has_frame, data = self._vid.read()
            if has_frame:
                self._preloaded_frames.append(data)

        self._vid.seek(self.frame)

    def _get_real_frame_count(self):
        self._vid.seek(0)
        counter = 0
        has_frame = True
        while has_frame:
            has_frame = self._vid.read()[0]
            if has_frame:
                counter += 1
        self._vid.seek(self.frame)
        return counter

    def _chunks_len(self, chunks):
        i = 0
        for c in chunks:
            if c is not None:
                i += 1
        return i

    def _convert_seconds(self, seconds):
        seconds = abs(seconds)
        d = str(seconds).split('.')[-1] if '.' in str(seconds) else 0
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{h}:{m}:{s}.{d}"
    
    # not used
    def _test_youtube(self):
        return YTDLP and next((ie.ie_key() for ie in yt_dlp.list_extractors() if ie.suitable(self.path) and ie.ie_key() != "Generic"), None) is not None
    
    # not used, not always accurate
    def _test_vfr(self):
        min_, max_ = self._get_vfrs(self._get_all_pts())[:2]
        return (max_ - min_) > 0.1

    def _test_no_audio(self):
        command = [
            "ffmpeg",
            "-i", self._audio_path,
            "-t", str(self._convert_seconds(0.1)),
            "-vn",
            "-f", "wav",
            "-loglevel", FFMPEG_LOGLVL,
            "-"
        ]

        audio = b''

        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE if self.as_bytes else None)
            audio = p.communicate(input=self.path if self.as_bytes else None)[0]

        except FileNotFoundError:
            self._missing_ffmpeg = True
            return

        return audio == b''

    def _threaded_load(self, index):
        i = index # assigned to variable so another thread does not change it

        self._chunks.append(None)

        s = (self._starting_time + (self._chunks_claimed - 1) * self.chunk_size) / (self.speed if not self.reverse else 1)

        if self.no_audio:
            command = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "anullsrc",
                "-t", str(self._convert_seconds(min(self.chunk_size, self.duration - s) / (self.speed if not self.reverse else 1))),
                "-f", "wav",
                "-loglevel", FFMPEG_LOGLVL,
                "-"
            ]

        else:

            command = [
                "ffmpeg",
                "-i", self._audio_path,
                "-ss", self._convert_seconds(s),
                "-t", self._convert_seconds(self.chunk_size / (self.speed if not self.reverse else 1)),
                "-vn",
                "-sn",
                "-map", f"0:a:{self.audio_track}",
                "-ac", str(self._audio.get_num_channels()) if self.use_pygame_audio else str(min(self.audio_channels, self._audio.get_num_channels())),
                "-f", "wav",
                "-loglevel", FFMPEG_LOGLVL,
                "-"
            ]

            filters = []
    
            # doesn't work when both are stacked
            # if they are, speed is handled post reversal

            if self.reverse:
                filters += ["-af", "areverse"]
            elif self.speed != 1:
                filters += ["-af", f"atempo={self.speed}"]
                #filters += ["-af", f"rubberband=tempo={self.speed}"]

            command = command[:7] + filters + command[7:]

        audio = None

        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE if self.as_bytes else None)
            self._processes.append(p)
            audio = p.communicate(input=self.path if self.as_bytes else None)[0]

            # apply speed change to already reversed audio chunk

            if not self.no_audio and self.speed != 1 and self.reverse:

                command = [
                    "ffmpeg",
                    "-i", "-",
                    "-af", f"atempo={self.speed}",
                    "-f", "wav",
                    "-loglevel", FFMPEG_LOGLVL,
                    "-"
                ]

                process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                self._processes.append(process)
                audio = process.communicate(input=audio)[0]
                self._processes.remove(process)

        except FileNotFoundError:
            self._missing_ffmpeg = True
            return
        
        self._processes.remove(p)
        self._chunks[i - self._chunks_played - 1] = audio

    def _update_threads(self):
        for t in self._threads:
            if not t.is_alive():
                self._threads.remove(t)

        self._stop_loading = self._starting_time + self._chunks_claimed * self.chunk_size >= self.duration
        if not self._stop_loading and (len(self._threads) < self.max_threads) and ((self._chunks_len(self._chunks) + len(self._threads)) < self.max_chunks):
            self._chunks_claimed += 1
            self._threads.append(Thread(target=self._threaded_load, args=(self._chunks_claimed,)))
            self._threads[-1].start()

    def _write_subs(self, p):
        for sub in self.subs:
            self._next_sub_line(sub, p)

    def _next_sub_line(self, sub, p):
        if p >= sub.start:
            if p > sub.end:
                if sub._get_next():
                    self._next_sub_line(sub, p)
            else:
                sub._write_subs(self.frame_surf)

    def _get_closest_frame(self, pts, ts):
        lo, hi = 0, len(pts) - 1
        best_ind = lo
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            if pts[mid] < ts:
                lo = mid + 1
            elif pts[mid] > ts:
                hi = mid - 1
            else:
                best_ind = mid
                break
            if abs(pts[mid] - ts) < abs(pts[best_ind] - ts):
                best_ind = mid
        if pts[best_ind] > ts and best_ind > 0:
            best_ind -= 1
        return best_ind
    
    def _has_frame(self, p):
        if self.vfr:
            return self.frame < self.frame_count and p > self.timestamps[self.frame]
        return p > self.frame / float(self.frame_rate)
    
    def _update(self):
        if self._missing_ffmpeg:
            raise FFmpegNotFoundError("Could not find FFmpeg. Make sure FFmpeg is installed and accessible via PATH.")

        self._update_threads()

        n = False
        self.buffering = False

        if self._audio.get_busy() or self.paused:

            p = self.get_pos()
            self._update_time = p

            while self._has_frame(p):
                data = None
                if self.reverse:
                    has_frame = True
                    try:
                        data = self._preloaded_frames[self.frame_count - self.frame - 1]
                    except IndexError:
                        has_frame = False
                else:

                    self.buffering = True
                    if self._preloaded:
                        has_frame = True
                        try:
                            data = self._preloaded_frames[self.frame]
                        except IndexError:
                            has_frame = False
                    else:
                        has_frame, data = self._vid.read()
                    self.buffering = False

                self.frame += 1

                # optimized for high playback speeds
                if self._has_frame(p):
                    continue

                if has_frame:
                    if self.original_size != self.current_size:
                        data = self._resize_frame(data, self.current_size, self.interp, not CV)
                    data = self.post_func(data)

                    self.frame_data = data
                    self.frame_surf = self._create_frame(data)

                    if self.subs and not self.subs_hidden:
                        self._write_subs(p)

                    n = True
                else:
                    break

        elif self.active:
            if self._chunks and self._chunks[0] is not None:
                self._chunks_played += 1
                tmp = self._chunks.pop(0)
                if self._chunks_played == 1 and self._buffer_first_chunk and self._buffered_chunk is None:
                    self._buffered_chunk = tmp
                self._audio.load(tmp)
                self._audio.play()
            elif self._stop_loading and self._chunks_played == self._chunks_claimed:
                self.stop()
            else:
                self.buffering = True # waiting for audio to load

        return n

    # interp parameter only used for ffmpeg resampling
    
    def _resize_frame(self, data: np.ndarray, size: Tuple[int, int], interp, use_ffmpeg=False):
        if not use_ffmpeg:
            return cv2.resize(data, dsize=size, interpolation=interp)

        # without opencv, use ffmpeg resizing

        if type(interp) == int:
            interp = ("neighbor", "bilinear", "bicubic", "area", "lanczos")[interp]

        try:
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-loglevel", str(FFMPEG_LOGLVL),
                    "-f", "rawvideo",
                    "-pix_fmt", "rgb24",
                    "-s", f"{data.shape[1]}x{data.shape[0]}",
                    "-i", "-",
                    "-vf", f"scale={size[0]}:{size[1]}:flags={interp}",
                    "-f", "rawvideo",
                    "-"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise FFmpegNotFoundError("Could not find FFmpeg. Make sure it's downloaded and accessible via PATH.")

        return np.frombuffer(process.communicate(input=data.tobytes())[0], np.uint8).reshape((size[1], size[0], 3))

    def probe(self) -> None:
        self._vid._probe(self.path, self.as_bytes)
        self.frame_count = self._vid.frame_count
        self.frame_rate = self._vid.frame_rate
        self.frame_delay = 1 / self.frame_rate
        self.duration = self._vid.duration
        self.original_size = self._vid.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

    def update(self) -> bool:
        return self._update()

    @property
    def volume(self):
        return self.get_volume()

    def set_interp(self, interp: Union[str, int]) -> None:
        if interp in ("nearest", 0):
            self.interp = 0 #cv2.INTER_NEAREST
        elif interp in ("linear", 1):
            self.interp = 1 #cv2.INTER_LINEAR
        elif interp in ("area", 3):
            self.interp = 3 #cv2.INTER_AREA
        elif interp in ("cubic", 2):
            self.interp = 2 #cv2.INTER_CUBIC
        elif interp in ("lanczos4", 4):
            self.interp = 4 #cv2.INTER_LANCZOS4
        else:
            raise ValueError("Interpolation technique not recognized.")

    def set_post_func(self, func: Callable[[np.ndarray], np.ndarray]) -> None:
        self.post_func = func

    def get_metadata(self):
        return {
            "path": self.path,
            "name": self.name,
            "ext": self.ext,
            "frame_rate": self.frame_rate,
            "vfr": self.vfr,
            "max_fr": self.max_fr,
            "min_fr": self.min_fr,
            "avg_fr": self.avg_fr,

            "frame_count": self.frame_count,
            "duration": self.duration,
            "original_size": self.original_size,
            "aspect_ratio": self.aspect_ratio,

            "audio_channels": self.audio_channels,
            "no_audio": self.no_audio

        }

    def mute(self) -> None:
        self.muted = True
        self._audio.mute()

    def unmute(self) -> None:
        self.muted = False
        self._audio.unmute()

    def set_speed(self, speed: float) -> None:
        raise DeprecationWarning("set_speed is deprecated. Use the speed parameter instead.")

    def get_speed(self) -> float:
        return self.speed

    def play(self) -> None:
        self.active = True
        if self._generated_frame:
            self._generated_frame = False
            self.seek_frame(self.frame)

    def stop(self) -> None:
        self.seek(0, relative=False)
        self.active = False
        # removing this to prevent flickering during loops
        # self.frame_data = None
        # self.frame_surf = None
        self.paused = False

    def resize(self, size: Tuple[int, int]) -> None:
        self.current_size = size
        if self.frame_data is not None:
            self.frame_data = self._resize_frame(self.frame_data, self.current_size, self.interp, not CV)
            self.frame_surf = self._create_frame(self.frame_data)

    def change_resolution(self, height: int) -> None:
        w = int(height * self.aspect_ratio)
        if w % 2 == 1:
            w += 1
        self.resize((w, height))

    def close(self) -> None:
        self._preloaded_frames.clear()
        self.stop()
        self._vid.release()
        self._audio.unload()
        if not self.use_pygame_audio:
            self._audio.close()
        self.closed = True

    def restart(self) -> None:
        self.seek(0, relative=False)

        if self._buffered_chunk is not None:
            self._chunks_claimed = 1
            self._chunks.append(self._buffered_chunk)

        self.play()

    def set_volume(self, vol: float) -> None:
        self._audio.set_volume(vol)

    def get_volume(self) -> float:
        return self._audio.get_volume()

    def get_paused(self) -> bool:
        # here because the original pyvidplayer had get_paused
        return self.paused

    def toggle_pause(self) -> None:
        self.resume() if self.paused else self.pause()

    def toggle_mute(self) -> None:
        self.unmute() if self.muted else self.mute()

    def set_audio_track(self, index: int) -> None:
        if self.youtube:
            return

        try:
            command = [
                "ffprobe",
                "-i", "-" if self.as_bytes else self.path,
                "-show_streams",
                "-select_streams", f"a:{index}",
                "-loglevel", FFMPEG_LOGLVL,
                "-print_format", "json"
            ]

            p = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if self.as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FFmpegNotFoundError(
                "Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate(input=self.path if self.as_bytes else None)[0])

        if len(info) == 0:
            raise VideoStreamError("Could not determine video.")
        info = info["streams"]
        if len(info) == 0:
            raise AudioStreamError(f"Audio index {index} out of range.")

        self.audio_channels = info[0]["channels"]
        self.audio_track = index
        self.seek(self.get_pos(), relative=False) # reloads current audio chunks

    def pause(self) -> None:
        if self.active:
            self.paused = True
            self._audio.pause()

    def resume(self) -> None:
        if self.active:
            self.paused = False
            self._audio.unpause()

    def get_pos(self) -> float:
        return self._starting_time + max(0, self._chunks_played - 1) * self.chunk_size + self._audio.get_pos() * self.speed

    def seek(self, time: float, relative: bool = True) -> None:
        # seeking accurate to 1/100 of a second

        self._starting_time = (self.get_pos() + time) if relative else time
        self._starting_time = min(max(0, self._starting_time), self.duration)

        for p in self._processes:
            p.kill()
        for t in self._threads:
            t.join()
            
        self._chunks.clear()
        self._threads.clear()
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._audio.unload()

        if self.vfr:
            self._vid.seek(self._get_closest_frame(self.timestamps, self._starting_time))
        else:
            frame = int(self._starting_time * self.frame_rate)
            if frame >= self.frame_count:
                frame = self.frame_count - 1
            self._vid.seek(frame)

        self.frame = self._vid.frame

        for sub in self.subs:
            sub._seek(self._starting_time)

    def seek_frame(self, index: int, relative: bool = False) -> None:
        # seeking accurate to 1/100 of a second
        index = (self.frame + index) if relative else index
        index = min(max(index, 0), self.frame_count - 1)

        if self.vfr:
            self._starting_time = self.timestamps[index]
        else:
            self._starting_time = min(max(0, index / self.frame_rate), self.duration)

        for p in self._processes:
            p.kill()
        for t in self._threads:
            t.join()

        self._chunks.clear()
        self._threads.clear()
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._audio.unload()
        self._vid.seek(index)

        self.frame = index

        for sub in self.subs:
            sub._seek(self._starting_time)

    def buffer_current(self) -> bool:
        if self._vid.frame > 0 and (self.frame_data is None or self.frame_surf is None):
            p = self.get_pos()
            self._vid.seek(self._vid.frame - 1)
            has_frame, data = self._vid.read()
            if has_frame:   # should theoretically never be false
                if self.original_size != self.current_size:
                    data = self._resize_frame(data, self.current_size, self.interp, not CV)
                data = self.post_func(data)

                self.frame_data = data
                self.frame_surf = self._create_frame(data)

                if self.subs and not self.subs_hidden:
                    self._write_subs(p)
                return True
        return False

    # type hints declared by inherited subclasses

    def draw(self, surf, pos, force_draw):
        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(surf, pos)
            return True
        return False
    
    # inherited methods

    @abstractmethod
    def _create_frame(self):
        pass

    @abstractmethod
    def _render_frame(self):
        pass

    @abstractmethod
    def preview(self):
        pass
