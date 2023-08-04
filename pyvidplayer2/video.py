import cv2 
import subprocess 
import os
from typing import Tuple 
from threading import Thread
from .pyaudio_handler import PyaudioHandler
from .post_processing import PostProcessing
from . import get_ffmpeg_path

try:
    import pygame 
except ImportError:
    pass
else:
    from .mixer_handler import MixerHandler


class Video:
    def __init__(self, path: str, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=True) -> None:
        
        self.path = path
        self.name, self.ext = os.path.splitext(os.path.basename(self.path))

        self._vid = cv2.VideoCapture(self.path)

        if not self._vid.isOpened():
            raise FileNotFoundError(f'Could not find "{self.path}"')

        # file information

        self.frame_count = int(self._vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self._vid.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1 / self.frame_rate
        self.duration = self.frame_count / self.frame_rate
        self.original_size = (int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.current_size = self.original_size
        self.aspect_ratio = self.original_size[0] / self.original_size[1]

        self.chunk_size = chunk_size
        self.max_chunks = max_chunks
        self.max_threads = max_threads

        self._chunks = []
        self._threads = []
        self._starting_time = 0
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._stop_loading = False

        self.frame_data = None
        self.frame_surf = None
        
        self.active = False
        self.buffering = False
        self.paused = False

        self.subs = subs
        self.post_func = post_process
        self.interp = interp

        if use_pygame_audio:
            try:
                self._audio = MixerHandler()
            except NameError:
                raise ModuleNotFoundError("Unable to use Pygame audio because Pygame is not installed.")
        else:    
            self._audio = PyaudioHandler()
        self.use_pygame_audio = use_pygame_audio
        
        self.play()

    def _chunks_len(self) -> int:
        i = 0
        for c in self._chunks:
            if c is not None:
                i += 1
        return i

    def _convert_seconds(self, seconds: float) -> str:
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        d = round(seconds % 1, 1)
        return f"{h}:{m}:{s}.{int(d * 10)}"

    def _threaded_load(self) -> None:
        self._chunks_claimed += 1
        i = self._chunks_claimed # assigned to variable so another thread does not change it

        self._chunks.append(None)

        s = self._convert_seconds(self._starting_time + (self._chunks_claimed - 1) * self.chunk_size)

        command = [
            get_ffmpeg_path(),
            "-i",
            self.path,
            "-ss",
            str(s),
            "-t",
            str(self._convert_seconds(self.chunk_size)),
            "-f",
            "wav",
            "-loglevel",
            "quiet",
            "-"
        ]

        p = subprocess.run(command, capture_output=True)
        
        self._chunks[i - self._chunks_played - 1] = p.stdout

    def _update_threads(self) -> None:
        for t in self._threads:
            if not t.is_alive():
                self._threads.remove(t)

        self._stop_loading = self._starting_time + self._chunks_claimed * self.chunk_size >= self.duration
        if not self._stop_loading and len(self._threads) < self.max_threads and self._chunks_len() + len(self._threads) < self.max_chunks:
            self._threads.append(Thread(target=self._threaded_load))
            self._threads[-1].start()

    def _write_subs(self) -> None:
        p = self.get_pos()
        
        if p >= self.subs.start:
            if p > self.subs.end:
                if self.subs._get_next():
                    self._write_subs()
            else:
                self.frame_surf.blit(self.subs.surf, (self.current_size[0] / 2 - self.subs.surf.get_width() / 2, self.current_size[1] - self.subs.surf.get_height() - 50))

    def _update(self) -> bool:
        self._update_threads()

        n = False
        self.buffering = False

        if self._audio.get_busy() or self.paused:

            while self.get_pos() > self._vid.get(cv2.CAP_PROP_POS_FRAMES) * self.frame_delay:

                has_frame, data = self._vid.read()
                
                if has_frame:
                    if self.original_size != self.current_size:
                        data = cv2.resize(data, dsize=self.current_size, interpolation=self.interp)
                    data = self.post_func(data)

                    self.frame_data = data
                    self.frame_surf = self._create_frame(data)

                    if self.subs is not None:
                        self._write_subs()

                    n = True
                else:
                    break

        elif self.active:
            if self._chunks and self._chunks[0] is not None:
                self._chunks_played += 1
                self._audio.load(self._chunks.pop(0))
                self._audio.play()
            elif self._stop_loading and self._chunks_played == self._chunks_claimed:
                self.stop()
            else:
                self.buffering = True
    
        return n
    
    def play(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.restart()
        self.active = False
        self.frame_data = None
        self.frame_surf = None

    def resize(self, size: Tuple[int, int]) -> None:
        self.current_size = size

    def change_resolution(self, height: int) -> None:
        self.current_size = (int(height * self.aspect_ratio), height)

    def close(self) -> None:
        self.stop()
        self._vid.release()
        self._audio.unload()
        for t in self._threads:
            t.join()

    def restart(self) -> None:
        self.seek(0, relative=False)
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

    def pause(self) -> None:
        if self.active:
            self.paused = True
            self._audio.pause()

    def resume(self) -> None:
        if self.active:
            self.paused = False
            self._audio.unpause()

    def get_pos(self) -> float:
        return min(self.duration, self._starting_time + max(0, self._chunks_played - 1) * self.chunk_size + self._audio.get_pos())

    def seek(self, time: float, relative=True) -> None:
        # seeking accurate to 1 tenth of a second

        self._starting_time = (self.get_pos() + time) if relative else time
        self._starting_time = round(min(max(0, self._starting_time), self.duration), 1)

        for t in self._threads:
            t.join()
        self._chunks = []
        self._threads = []
        self._chunks_claimed = 0
        self._chunks_played = 0
        self._audio.unload()

        self._vid.set(cv2.CAP_PROP_POS_FRAMES, self._starting_time * self.frame_rate)
        if self.subs is not None:
            self.subs._seek(self._starting_time)

    def draw(self, surf, pos: Tuple[int, int], force_draw=True) -> bool:
        if self._update() or force_draw:
            if self.frame_surf is not None:
                self._render_frame(surf, pos)
                return True
        return False

    def _create_frame(self):
        pass
    
    def _render_frame(self):
        pass
    
    def preview(self):
        pass 

