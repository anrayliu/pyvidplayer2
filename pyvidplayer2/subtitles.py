import subprocess
import pygame
import pysubs2
import re
import os
from typing import Union, Tuple
from . import FFMPEG_LOGLVL
from .error import *

try:
    import yt_dlp
except ModuleNotFoundError:
    YTDLP = 0
else:
    YTDLP = 1


class Subtitles:
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """

    def __init__(self, path: str, colour: Union[str, pygame.Color, Tuple[int, int, int]] = "white", highlight: Tuple[int, int, int, int] = (0, 0, 0, 128), 
                 font: Union[pygame.font.SysFont, pygame.font.Font] = None, encoding: str = "utf-8", offset: int = 50,
                 delay: float = 0, youtube: bool = False, pref_lang: str = "en", track_index: int = None) -> None:
        
        self.path = path
        self.track_index = track_index
        self.encoding = encoding

        self.youtube = youtube
        self.pref_lang = pref_lang
        self._auto_cap = False
        self.buffer = ""
        if youtube:
            if YTDLP:
                self.buffer = self._extract_youtube_subs()
            else:

                raise ModuleNotFoundError("Unable to fetch subtitles because YTDLP is not installed. YTDLP can be installed via pip.")
        else:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"[Errno 2] No such file or directory: '{self.path}'")

            if track_index is not None:
                if not os.path.exists(self.path):
                    raise FileNotFoundError(f"[Errno 2] No such file or directory: '{self.path}'")

                self.buffer = self._extract_internal_subs()
                if self.buffer == "":
                    raise SubtitleError("Could not find selected subtitle track in video.")

        self._subs = self._load()

        self.start = 0
        self.end = 0
        self.text = ""
        self.surf = pygame.Surface((0, 0))
        self.offset = offset
        self.delay = delay

        self.colour = colour
        self.highlight = highlight 

        self.font = None
        self.set_font(pygame.font.SysFont("arial", 30) if font is None else font)


    def __str__(self):
        return f"<Subtitles(path={self.path})>"

    def _load(self):
        try:
            if self.buffer != "":
                return iter(pysubs2.SSAFile.from_string(self.buffer))
            return iter(pysubs2.load(self.path, encoding=self.encoding))
        except (pysubs2.exceptions.FormatAutodetectionError, UnicodeDecodeError):
            raise SubtitleError("Could not load subtitles. Unknown format or corrupt file. Check that the proper encoding format is set.")

    def _to_surf(self, text):
        h = self.font.get_height()

        lines = text.splitlines()
        surfs = [self.font.render(line, True, self.colour) for line in lines]

        surface = pygame.Surface((max([s.get_width() for s in surfs]), len(surfs) * h), pygame.SRCALPHA)
        surface.fill(self.highlight)
        for i, surf in enumerate(surfs):
            surface.blit(surf, (surface.get_width() / 2 - surf.get_width() / 2, i * h))

        return surface

    def _extract_internal_subs(self):
        try:
            p = subprocess.Popen(f"ffmpeg -i {self.path} -loglevel {FFMPEG_LOGLVL} -map 0:s:{self.track_index} -f srt -", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FFmpegNotFoundError("Could not find FFmpeg. Make sure FFmpeg is installed and accessible via PATH.")

        return "\n".join(p.communicate()[0].decode(self.encoding).splitlines())

    def _extract_youtube_subs(self):
        cfg = {
            "quiet":True,
            "skip_download": True,
            "writeautomaticsub": True,
            "subtitleslangs": [self.pref_lang],
            "subtitlesformat": "vtt"
        }

        with yt_dlp.YoutubeDL(cfg) as ydl:
            info = ydl.extract_info(self.path, download=False)

            subs = info.get("subtitles", {})
            if not self.pref_lang in subs:
                subs = info.get("automatic_captions", {})

                self._auto_cap = True

            if self.pref_lang in subs:
                for i, s in enumerate(subs[self.pref_lang]):
                    if s["ext"] == "vtt":
                        return ydl.urlopen(subs[self.pref_lang][i]["url"]).read().decode("utf-8")
            else:
                raise SubtitleError("Could not find subtitles in the specified language.")

    def _get_next(self):
        try:
            s = next(self._subs)
        except StopIteration:
            self.start = 0 + self.delay
            self.end = 0 + self.delay
            self.text = ""
            self.surf = pygame.Surface((0, 0))
            return False
        else:
            self.start = s.start / 1000 + self.delay
            self.end = s.end / 1000 + self.delay
            self.text = (re.sub(r"<\b\d+:\d+:\d+(?:\.\d+)?\b>", "", s.plaintext.split("\n")[1] if "\n" in s.plaintext else s.plaintext).replace("[&nbsp;__&nbsp;]", "[__]") if self._auto_cap else s.plaintext).strip()
            if self.text != "":
                self.surf = self._to_surf(self.text)
            return True

    def _seek(self, time):
        self._subs = self._load()

        self.end = 0 + self.delay
        self.start = 0 + self.delay
        self.text = ""
        self.surf = pygame.Surface((0, 0))

        while self.end < time:
            if not self._get_next():
                break

    def _write_subs(self, surf):
        surf.blit(self.surf, (surf.get_width() / 2 - self.surf.get_width() / 2, surf.get_height() - self.surf.get_height() - self.offset))
        
    def set_font(self, font: Union[pygame.font.SysFont, pygame.font.Font]) -> None:
        self.font = font
        if not isinstance(self.font, pygame.font.Font):
            raise ValueError("Font must be a pygame.font.Font or pygame.font.SysFont object.")

    def get_font(self) -> Union[pygame.font.SysFont, pygame.font.Font]:
        return self.font
