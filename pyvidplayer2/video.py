# Contains most of the core logic for video playback
# This project started when I was a lot less experienced,
# and over the years, it's greatly surpassed my initial scope.
# As such, the code quality can be lacking - it's an
# active challenge to make better refactors

import importlib.util
import json
import os
import subprocess
from abc import abstractmethod
from threading import Thread
from typing import Callable, Tuple, Union

import numpy as np

from . import get_ffmpeg_loglevel, get_ffmpeg_path, get_ffprobe_path
from .error import (AudioStreamError, FFmpegNotFoundError, OpenCVError,
                    VideoStreamError, YTDLPError, Pyvidplayer2Error)
from .ffmpeg_reader import FFMPEGReader

CV = 0
if importlib.util.find_spec("cv2") is not None:
    CV = 1
    import cv2

    from .cv_reader import CVReader

# pyaudio is obsolete, replaced with python sounddevice

# try:
#     import pyaudio
# except ImportError:
#     PYAUDIO = 0
# else:
#     PYAUDIO = 1
#     from .pyaudio_handler import PyaudioHandler

SOUNDDEVICE = 0
if importlib.util.find_spec("sounddevice") is not None:
    SOUNDDEVICE = 1
    from .psd_handler import PSDHandler

PYGAME = 0
SUBS = 0
if importlib.util.find_spec("pygame") is not None:
    PYGAME = 1
    from .mixer_handler import MixerHandler

    if importlib.util.find_spec("pysubs2") is not None:
        SUBS = 1
        from .subtitles import Subtitles

YTDLP = 0
if importlib.util.find_spec("yt_dlp") is not None:
    YTDLP = 1
    import yt_dlp

IIO = 0
if importlib.util.find_spec("imageio") is not None:
    IIO = 1
    from .imageio_reader import IIOReader

DECORD = 0
if importlib.util.find_spec("decord") is not None:
    DECORD = 1
    from .decord_reader import DecordReader


# for specifying different reader backends
READER_AUTO = 0
READER_FFMPEG = 1
READER_OPENCV = 2
READER_IMAGEIO = 3
READER_DECORD = 4


class Video:
    """Base class for video playback. Videos can be read from
    disk, RAM, or streamed from YouTube. Videos can only be played
    simultaneously if using Sounddevice as the audio library. Pygame or
    Pygame CE are the only graphics libraries to support subtitles.
    yt-dlp is required to stream videos from YouTube. Decord is required to
    play videos from RAM."""

    def __init__(self, path, chunk_size, max_threads, max_chunks, subs,
                 post_process, interp, use_pygame_audio, reverse,
                 no_audio, speed, youtube, max_res, as_bytes, audio_track, vfr,
                 pref_lang, audio_index, reader,
                 cuda_device) -> None:

        self._audio_path = path  # used for audio only when streaming

        self.path = path
        self.name = ""
        self.ext = ""

        as_bytes = as_bytes or isinstance(path, bytes)

        # automatic youtube url detection
        # disabled because it adds too much overhead to be implicit
        # youtube = youtube or self._test_youtube()

        self.pref_lang = pref_lang

        # default -1 for no cuda hw acceleration
        self.cuda_device = cuda_device
        if self.cuda_device >= 0 and reader != READER_FFMPEG:
            raise Pyvidplayer2Error("Must use FFmpeg reader for cuda devices.")

        # determines correct video backend here
        reader = self._get_best_reader(youtube, as_bytes, reader)
        if youtube:
            if not YTDLP:
                raise ModuleNotFoundError(
                    "Unable to stream video because YTDLP is not installed. Refer to https://github.com/anrayliu/pyvidplayer2/blob/main/examples/youtube_streaming_demo.py for instructions.")

            # sets path and audio path for cv2 and ffmpeg
            # also sets name and ext
            self._set_stream_url(path, max_res)

            # cannot use ffmpeg reader and therefore cuda device here
            self._vid = reader(self.path)

            # having less than 60 hurts performance
            chunk_size = max(chunk_size, 60)
            max_threads = min(max_threads, 1)

        elif as_bytes:
            # cannot use ffmpeg reader and therefore cuda device here
            self._vid = reader(self.path)
            self._audio_path = "-"  # read from pipe

        else:
            if not os.path.exists(self.path):
                raise FileNotFoundError(
                    f"[Errno 2] No such file or directory: '{self.path}'")

            self._vid = reader(self.path, cuda_device=cuda_device) if reader == FFMPEGReader else reader(self.path)
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
        self.num_audio_tracks = 0

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
        self.use_pygame_audio = use_pygame_audio  # or (PYGAME and not PYAUDIO)
        self.youtube = youtube
        self.max_res = max_res
        self.as_bytes = as_bytes
        self.audio_track = audio_track
        self.vfr = vfr  # or self._test_vfr()
        self.audio_index = audio_index

        # select correct audio backend
        if self.use_pygame_audio:
            if not PYGAME:
                raise ModuleNotFoundError(
                    "Pygame is not installed. Install it via pip or use a different audio backend.")

            self._audio = MixerHandler()
        else:
            if not SOUNDDEVICE:
                raise ModuleNotFoundError(
                    "Python-sounddevice is not installed. Install it via pip or use a different audio backend.")

            # self._audio = PyaudioHandler()
            self._audio = PSDHandler()

            if self.audio_index is not None:
                self._audio._set_device_index(self.audio_index)

        self.speed = float(max(0.25, min(10, speed)))
        self.reverse = reverse
        self.no_audio = no_audio or self._test_no_audio()

        self._missing_ffmpeg = False  # for throwing errors
        self._skipped_frame = False  # used when slicing
        self._skipped_frame_index = 0  # used when slicing
        self._seek_buffered = False
        self._preloaded = False
        self._update_time = 0.0  # for testing

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

    def __len__(self) -> int:
        return self.frame_count

    def __str__(self) -> str:
        return f"<{type(self).__name__}(path={self.path if not (self.as_bytes or self.youtube) else ''})>"

    # noinspection PyUnresolvedReferences
    def __enter__(self) -> "pyvidplayer2.Video":  # noqa: F821
        return self

    def __exit__(self, type_, value, traceback) -> None:
        self.close()

    # noinspection PyUnresolvedReferences
    def __iter__(self) -> "pyvidplayer2.Video":  # noqa: F821
        self.stop()
        return self

    def __getitem__(self, item) -> np.ndarray:
        if isinstance(item, slice):
            raise TypeError("Slicing is not supported.")

        if item >= self.frame_count or item < -self.frame_count:
            raise IndexError("Index out of bounds.")
        if item < 0:
            item = self.frame_count + item

        if not self._skipped_frame:
            self._skipped_frame_index = self.frame
            self._skipped_frame = True

        self.seek_frame(item)  # keep intuitive seeking here
        return self.frame_data

    def __next__(self) -> np.ndarray:
        self._skipped_frame_index = self.frame
        self._skipped_frame = True

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
            self._skipped_frame_index += 1
            if self.original_size != self.current_size:
                data = self._resize_frame(data, self.current_size, self.interp, not CV)
            data = self.post_func(data)

            return data

        raise StopIteration("No more frames to read.")

    def _get_best_reader(self, youtube, as_bytes, reader):
        """
        Decides the best reader to use based on what's installed
        """
        if youtube:
            if reader in (READER_AUTO, READER_OPENCV):
                if CV:
                    return CVReader
                if reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "Unable to stream video because OpenCV is not installed. OpenCV can be installed via pip.")
            raise ValueError(
                "Only READER_OPENCV is supported for Youtube videos.")
        elif as_bytes:
            if reader in (READER_AUTO, READER_DECORD):
                if DECORD:
                    return DecordReader
                if reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "Unable to read video from memory because decord is not installed. "
                        "Decord can be installed via pip.")
            if reader in (READER_AUTO, READER_IMAGEIO):
                if IIO:
                    return IIOReader
                if reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "Unable to read video from memory because IMAGEIO is not installed. "
                        "IMAGEIO can be installed via pip.")
            raise ValueError(
                "Only READER_DECORD and READER_IMAGEIO is supported for reading from memory.")
        else:
            if reader in (READER_AUTO, READER_OPENCV):
                if CV:
                    return CVReader
                if reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "OpenCV is not installed. OpenCV can be installed through pip.")
            if reader in (READER_AUTO, READER_DECORD):
                if DECORD:
                    return DecordReader
                if reader != READER_AUTO:
                    raise ModuleNotFoundError(
                        "Decord is not installed. Decord can be installed through pip.")
            if reader in (READER_AUTO, READER_FFMPEG):
                return FFMPEGReader
            if reader == READER_IMAGEIO:
                if IIO:
                    return IIOReader
                raise ModuleNotFoundError(
                    "ImageIO is not installed. ImageIO can be installed through pip.")
            raise ValueError("Could not identify backend.")

    def _filter_subs(self, subs):
        if SUBS and isinstance(subs, Subtitles):
            return [subs]
        return [] if subs is None else subs

    def _get_vfrs(self, pts):
        """
        Return minimum frame rate, maximum frame rate, and average frame rate from a video.
        Only useful for VFR videos
        """

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
        """
        Returns the presentation timestamps for each frame
        """

        try:
            command = [
                get_ffprobe_path(),
                "-i", "-" if self.as_bytes else self.path,
                "-select_streams", "v:0",
                "-show_entries", "packet=pts_time",
                "-loglevel", get_ffmpeg_loglevel(),
                "-print_format", "json"
            ]

            with subprocess.Popen(
                    command, stdin=subprocess.PIPE if self.as_bytes else None, stdout=subprocess.PIPE) as p:
                info = json.loads(p.communicate(input=self.path if self.as_bytes else None)[0])
        except FileNotFoundError as e:
            raise FFmpegNotFoundError(
                "Could not find FFprobe (should be bundled with FFmpeg). "
                "Make sure FFprobe is installed and accessible via PATH.") from e

        pts = sorted([float(dict_["pts_time"]) for dict_ in info["packets"]])
        if pts:
            offset = pts[0]
            pts = [t - offset for t in pts]

        return pts

    # mainly for testing purposes
    def _force_ffmpeg_reader(self):
        """
        Force switches reader to READER_FFMPEG
        """
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
            except Exception as e:  # something went wrong with yt_dlp
                if "Requested format is not available" in str(e):
                    raise YTDLPError("Could not find requested resolution.") from e
                raise YTDLPError(
                    "yt-dlp could not open video. Please ensure the URL is a valid Youtube video.") from e

            self.path = formats[0]["url"]
            self._audio_path = formats[1]["url"]
            self.name = info.get("title", "")
            self.ext = ".webm"

    def _preload_frames(self):
        """
        Decodes every frame and stores them in video._preloaded attribute
        """
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
        """
        Returns an accurate frame count by reading every frame
        """

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
        return sum(1 for c in chunks if c is not None)

    def _convert_seconds(self, seconds):
        seconds = abs(seconds)
        d = str(seconds).rsplit('.', maxsplit=1)[-1] if '.' in str(seconds) else 0
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{h}:{m}:{s}.{d}"

    # not used
    # used to auto detect youtube videos

    # def _test_youtube(self):
    #     return YTDLP and next(
    #         (ie.ie_key() for ie in yt_dlp.list_extractors() if ie.suitable(self.path) and ie.ie_key() != "Generic"),
    #         None) is not None

    # not used, not always accurate
    # used to auto detect vfr videos

    # def _test_vfr(self):
    #     min_, max_ = self._get_vfrs(self._get_all_pts())[:2]
    #     return (max_ - min_) > 0.1

    def _test_no_audio(self):
        """
        Returns True if video has no audio
        """
        command = [
            get_ffmpeg_path(),
            "-i", self._audio_path,
            "-t", str(self._convert_seconds(0.1)),
            "-vn",
            "-f", "wav",
            "-loglevel", get_ffmpeg_loglevel(),
            "-"
        ]

        try:
            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE if self.as_bytes else None) as p:
                audio = p.communicate(input=self.path if self.as_bytes else None)[0]

        except FileNotFoundError:
            self._missing_ffmpeg = True
            return

        return audio == b''

    def _get_num_channels_to_process(self):
        return min(self.audio_channels, self._audio.get_num_channels())

    def _threaded_load(self, index):
        i = index  # assigned to variable so another thread does not change it

        # save a spot in the list to prevent other threads from messing up the order
        # append is atomic
        self._chunks.append(None)

        s = (self._starting_time + (self._chunks_claimed - 1) * self.chunk_size) / (
            self.speed if not self.reverse else 1)

        if self.no_audio:
            # generates silent audio
            # very important because audio-visual syncing is done by tracking played audio chunks

            command = [
                get_ffmpeg_path(),
                "-f", "lavfi",
                "-i", "anullsrc",
                # if chunk_size==5 and speed==2, 10 seconds of silent audio will be generated
                "-t", self._convert_seconds(min(self.chunk_size, self.duration - s) / self.speed),
                "-f", "wav",
                "-loglevel", get_ffmpeg_loglevel(),
                "-"
            ]

        else:
            command = [
                get_ffmpeg_path(),
                "-i", self._audio_path,
                "-ss", self._convert_seconds(s),
                "-t", self._convert_seconds(self.chunk_size / (self.speed if not self.reverse else 1)),
                "-vn",
                "-sn",
                "-map", f"0:a:{self.audio_track}",

                # sounddevice can get number of channels output device has, allowing
                # ffmpeg to remix audio to match

                "-ac", str(self._get_num_channels_to_process()),
                "-f", "wav",
                "-loglevel", get_ffmpeg_loglevel(),
                "-"
            ]

            filters = []

            # doesn't work when both are stacked
            # if they are, speed is handled post reversal

            if self.reverse:
                filters += ["-af", "areverse"]
            elif self.speed != 1:
                filters += ["-af", f"atempo={max(0.5, self.speed)}"]
                if self.speed < 0.5:
                    filters[-1] += f",atempo={self.speed/0.5}"

                # rubberband is more intensive
                # filters += ["-af", f"rubberband=tempo={self.speed}"]

            command = command[:7] + filters + command[7:]

        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE if self.as_bytes else None)
            self._processes.append(p)
            audio = p.communicate(input=self.path if self.as_bytes else None)[0]

            # apply speed change to already reversed audio chunk

            if not self.no_audio and self.speed != 1 and self.reverse:
                command = [
                    get_ffmpeg_path(),
                    "-i", "-",
                    "-af", f"atempo={max(0.5, self.speed)}",
                    "-f", "wav",
                    "-loglevel", get_ffmpeg_loglevel(),
                    "-"
                ]
                if self.speed < 0.5:
                    command[4] += f",atempo={self.speed/0.5}"

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
        if not self._stop_loading and (len(self._threads) < self.max_threads) and (
                (self._chunks_len(self._chunks) + len(self._threads)) < self.max_chunks):
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
        low, high = 0, len(pts) - 1
        index = low
        while low <= high:
            mid = low + (high - low) // 2
            if pts[mid] < ts:
                low = mid + 1
            elif pts[mid] > ts:
                high = mid - 1
            else:
                index = mid
                break
            if abs(pts[mid] - ts) < abs(pts[index] - ts):
                index = mid
        if pts[index] > ts and index > 0:
            index -= 1
        return index

    def _has_frame(self, p):
        if self.vfr:
            return self.frame < self.frame_count and p > self.timestamps[self.frame]
        return p > self.frame / float(self.frame_rate)

    # driving function behind video playback
    def _update(self):
        if self._missing_ffmpeg:
            raise FFmpegNotFoundError(
                "Could not find FFmpeg. Make sure FFmpeg is installed and accessible via PATH.")

        self._update_threads()

        n = False
        if self._seek_buffered:
            n = True
            self._seek_buffered = False
        self.buffering = False  # used by video player objects

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

                # optimized for high playback speeds by
                # avoiding redundant calculations for skipped frames
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
                self.buffering = True  # waiting for audio to load

        return n

    # interp parameter only used for ffmpeg resampling

    def _resize_frame(self, data: np.ndarray, size: Tuple[int, int], interp, use_ffmpeg=False):
        """
        Given a numpy image, returns a new resized numpy image.
        If not using ffmpeg, pass in cv2 interpolation constants (e.g INTER_NEAREST)
        If using ffmepg, consult their documentation for interpolation flags.
        """

        if not use_ffmpeg:
            return cv2.resize(data, dsize=size, interpolation=interp)

        # without opencv, use ffmpeg resizing

        if isinstance(interp, int):
            interp = ("neighbor", "bilinear", "bicubic", "area", "lanczos")[interp]

        try:
            with subprocess.Popen(
                    [
                        get_ffmpeg_path(),
                        "-loglevel", get_ffmpeg_loglevel(),
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
            ) as p:
                return np.frombuffer(p.communicate(input=data.tobytes())[0], np.uint8).reshape((size[1], size[0], 3))
        except FileNotFoundError as e:
            raise FFmpegNotFoundError(
                "Could not find FFmpeg. Make sure it's downloaded and accessible via PATH.") from e

    def probe(self) -> None:
        """Use FFprobe to find information about the video. When using OpenCV
        to read videos, information such as frame count and frame rate are
        read through the file headers, which is sometimes incorrect.
        For more accuracy, call this method to start a probe and update video
        metadata attributes."""

        self._vid._probe(self.path, self.as_bytes)
        self.frame_count = self._vid.frame_count
        self.frame_rate = self._vid.frame_rate
        self.frame_delay = 1 / self.frame_rate
        self.duration = self._vid.duration
        self.original_size = self._vid.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

    def update(self) -> bool:
        """Allow video to perform required calculations. Draw automatically
        calls this method, so it doesn't need to be explicitly called.
        Returns True if a new frame is ready to be displayed."""

        return self._update()

    @property
    def volume(self):
        return self.get_volume()

    def set_interp(self, interp: Union[str, int]) -> None:
        """Set the interpolation technique for frame resizing. Accepts nearest,
         linear, cubic, lanczos4, area. Nearest is the fastest technique but
         produces the worst results. Lanczos4 produces the best results but is
         much more compute-intensive. Area is a technique that produces the
         best results when downscaling. This parameter can also accept
         OpenCV constants like cv2.INTER_LINEAR."""

        if interp in ("nearest", 0):
            self.interp = 0  # cv2.INTER_NEAREST
        elif interp in ("linear", 1):
            self.interp = 1  # cv2.INTER_LINEAR
        elif interp in ("area", 3):
            self.interp = 3  # cv2.INTER_AREA
        elif interp in ("cubic", 2):
            self.interp = 2  # cv2.INTER_CUBIC
        elif interp in ("lanczos4", 4):
            self.interp = 4  # cv2.INTER_LANCZOS4
        else:
            raise ValueError("Interpolation technique not recognized.")

    def set_post_func(self, func: Callable[[np.ndarray], np.ndarray]) -> None:
        """Change the post-processing function. Works the same as the
        post_func parameter."""

        self.post_func = func

    def get_metadata(self):
        """Output a dictionary with attributes about the file metadata,
        including frame_count, frame_rate, etc."""

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
            "num_audio_tracks": self.num_audio_tracks,
            "no_audio": self.no_audio
        }

    def mute(self) -> None:
        """Mute audio playback. Does not affect volume."""

        self.muted = True
        self._audio.mute()

    def unmute(self) -> None:
        """Unmute audio playback. Does not affect volume."""

        self.muted = False
        self._audio.unmute()

    def set_speed(self, speed: float) -> None:
        """Set a new speed value (0.25-10.0)."""

        speed = float(max(0.25, min(10, speed)))
        self.seek_frame(0, relative=True, intuitive=False)
        self.speed = speed

    def get_speed(self) -> float:
        """
        Return current video speed.
        """

        return self.speed

    def play(self) -> None:
        """Set the video as active and begin playback."""

        self.active = True
        if self._skipped_frame:
            self.seek_frame(self._skipped_frame_index, intuitive=False)
            self._skipped_frame = False  # reset flags
            self._skipped_frame_index = 0

    def stop(self) -> None:
        """Stop video playback and rewind to the beginning.
        Sets active state to False but does not change the paused state."""

        self.seek(0, relative=False, intuitive=False)
        self.active = False
        # removing this to prevent flickering during loops
        # self.frame_data = None
        # self.frame_surf = None
        self.paused = False

    def resize(self, size: Tuple[int, int]) -> None:
        """Resize video frames to new dimensions. This will also resize the
        current frame."""

        self.current_size = size
        if self.frame_data is not None:
            self.frame_data = self._resize_frame(self.frame_data, self.current_size, self.interp, not CV)
            self.frame_surf = self._create_frame(self.frame_data)

    def change_resolution(self, height: int) -> int:
        """Given a height, the video will scale its dimensions while
        maintaining aspect ratio. Returns the new width."""

        w = int(height * self.aspect_ratio)
        if w % 2 == 1:
            w += 1
        self.resize((w, height))

        return w

    def close(self) -> None:
        """Release resources and closes the video. Always recommended to call
        when done. Attempting to use the video after closing may cause
        unexpected behaviour."""

        self._preloaded_frames.clear()
        self.path = ""  # clears byte buffer
        self.stop()
        self._vid.release()
        self._audio.close()
        self.closed = True

    def restart(self) -> None:
        """Rewind video to the beginning. Does not change the active state."""

        self.seek(0, relative=False, intuitive=True)

        if self._buffered_chunk is not None:
            self._chunks_claimed = 1
            self._chunks.append(self._buffered_chunk)

        self.play()

    def set_volume(self, vol: float) -> None:
        """Adjust the volume of the video, from 0.0 (min) to 1.0 (max)."""

        self._audio.set_volume(vol)

    def get_volume(self) -> float:
        """Return current video volume."""

        return self._audio.get_volume()

    def get_paused(self) -> bool:
        """Return whether the video is paused."""

        return self.paused

    def toggle_pause(self) -> None:
        """Toggle between paused and playing states."""

        if self.paused:
            self.resume()
        else:
            self.pause()

    def toggle_mute(self) -> None:
        """Toggle between muted and unmuted states."""

        if self.muted:
            self.unmute()
        else:
            self.mute()

    def set_audio_track(self, index: int) -> None:
        """Select which audio track to use for playback.
        Index 0 selects the first, 1 the second, etc."""

        if self.youtube:
            return

        try:
            command = [
                get_ffprobe_path(),
                "-i", "-" if self.as_bytes else self.path,
                "-show_streams",
                "-select_streams", "a",
                "-loglevel", get_ffmpeg_loglevel(),
                "-print_format", "json"
            ]

            with subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE if self.as_bytes else None,
                    stdout=subprocess.PIPE) as p:
                info = json.loads(p.communicate(input=self.path if self.as_bytes else None)[0])
        except FileNotFoundError as e:
            raise FFmpegNotFoundError(
                "Could not find FFprobe (should be bundled with FFmpeg). "
                "Make sure FFprobe is installed and accessible via PATH.") from e

        if len(info) == 0:
            raise VideoStreamError("Could not determine video.")
        info = info["streams"]

        if index < 0 or index > len(info) - 1:
            raise AudioStreamError(f"Audio index {index} out of range.")

        self.audio_channels = info[index]["channels"]
        self.num_audio_tracks = len(info)
        self.audio_track = index
        self.seek(self.get_pos(), relative=False, intuitive=False)  # reloads current audio chunks

    def pause(self) -> None:
        """Pause the video."""

        if self.active:
            self.paused = True
            self._audio.pause()

    def resume(self) -> None:
        """Resume playback of a paused video."""

        if self.active:
            self.paused = False
            self._audio.unpause()

    def get_pos(self) -> float:
        """Return the current video timestamp/position in decimal seconds."""

        return self._starting_time + max(0, self._chunks_played - 1) * self.chunk_size + self._audio.get_pos() * self.speed

    def seek(self, time: float, relative: bool = True, intuitive: bool = True) -> None:
        """Change the current position in the video. If relative is True,
        the given time will be added or subtracted to the current time.
        Otherwise, the current position will be set to the given time exactly.
        Time must be given in seconds, with a precision limit of 3 decimals.
        If the given value is larger than the video duration, the video will
        seek to the last frame. Remember that the frame attribute represents
        the next frame to be rendered. Most people expect seeking to already
        display the frame they want, but this will require incrementing frame
        by one extra. To force frame to be exactly correct (which is one frame
        before requested position), set intuitive to False. Intuitive seeking
        does not work for Raylib and wxPython."""

        self._starting_time = (self.get_pos() + time) if relative else time
        self._starting_time = round(self._starting_time, 3)
        self._starting_time = min(max(0, self._starting_time), self.duration)

        for p in self._processes:
            # borrow method to cleanly close processes
            FFMPEGReader._end_proc(p)
        for t in self._threads:
            t.join()

        self._chunks.clear()
        self._threads.clear()
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._audio.unload()

        self.frame_data = None
        self.frame_surf = None

        if self.vfr:
            frame = self._get_closest_frame(self.timestamps, self._starting_time)
        else:
            frame = int(self._starting_time * self.frame_rate)
            if frame >= self.frame_count:
                frame = self.frame_count - 1
        if intuitive and not relative:
            frame += 1
        self._vid.seek(frame)

        self.frame = self._vid.frame

        for sub in self.subs:
            sub._seek(self._starting_time)

        self.buffer_current()

    def seek_frame(self, index: int, relative: bool = False, intuitive: bool = True) -> None:
        """Seek to a specific frame. Index 0 will seek to the first frame, 1 to
         the second, etc. If the given index is larger than the total frames,
         the video will seek to the last frame. Remember that the frame
         attribute represents the next frame to be rendered. Most people
         expect seeking to display the frame they want, but this will require
         incrementing frame by one extra. To force frame to be exactly correct
         (which is one frame before requested position), set intuitive to
         False. Intuitive seeking does not work for Raylib and wxPython."""

        index = (self.frame + index) if relative else index
        index = min(max(index, 0), self.frame_count - 1)

        if self.vfr:
            self._starting_time = self.timestamps[index]
        else:
            self._starting_time = min(max(0, index / self.frame_rate), self.duration)

        for p in self._processes:
            # borrow method to cleanly close processes
            FFMPEGReader._end_proc(p)
        for t in self._threads:
            t.join()

        self._chunks.clear()
        self._threads.clear()
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._audio.unload()

        self.frame_data = None
        self.frame_surf = None

        # Technically, video.frame represents the next frame that will be rendered.
        # When seeking to a frame, if video.frame were to match index exactly, the
        # desired frame by definition, will yet to be rendered. This may be unintuitive for most,
        # as if you seek to a frame, you expect to be able to see the frame.
        # Therefore, I'm adding this intuitive parameter so users can choose the behaviour they want.

        if intuitive and not relative:
            index += 1

        self._vid.seek(index)

        self.frame = index

        for sub in self.subs:
            sub._seek(self._starting_time)

        self.buffer_current()

    def buffer_current(self) -> bool:
        """Populate frame_data and frame_surf if they are currently None.
        As of v0.9.32, this is automatically called when seeking."""

        if self.frame_data is not None and self.frame_surf is not None:
            return False

        p = self.get_pos()
        has_frame = False
        data = None

        if self.reverse:
            # at least one frame was rendered already - there's something to buffer
            if self.frame > 0:
                has_frame = True
                data = self._preloaded_frames[self.frame_count - self.frame]

        # same check here
        elif self._vid.frame > 0:
            self._vid.seek(self._vid.frame - 1)
            has_frame, data = self._vid.read()

        if has_frame:
            if self.original_size != self.current_size:
                data = self._resize_frame(data, self.current_size, self.interp, not CV)
            data = self.post_func(data)

            self.frame_data = data
            self.frame_surf = self._create_frame(data)

            if self.subs and not self.subs_hidden:
                self._write_subs(p)
            self._seek_buffered = True

            return True

        return False

    # type hints declared by inherited subclasses

    def draw(self, surf, pos, force_draw):
        """Draw the current video frame onto the given surface, at the given
        position. If force_draw is True, a surface will be drawn every time
        this is called. Otherwise, only new frames will be drawn. This reduces
        CPU usage but will cause flickering if anything is drawn under or above
        the video. This method returns whether a frame was drawn."""

        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(surf, pos)
            return True
        return False

    # inherited methods

    @abstractmethod
    def _create_frame(self, *args):
        pass

    @abstractmethod
    def _render_frame(self, *args):
        pass

    @abstractmethod
    def preview(self, *args):
        """Open a window and play the video. This method will hang until the
        video finishes or the window is closed."""
