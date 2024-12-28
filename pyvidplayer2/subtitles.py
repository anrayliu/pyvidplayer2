import subprocess
import pygame
import pysubs2
import re
from typing import Union, Tuple
from . import FFMPEG_LOGLVL

try:
    import yt_dlp
except ModuleNotFoundError:
    YTDLP = 0
else:
    YTDLP = 1


class Subtitles:
    '''
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    '''

    def __init__(self, path: str, colour: Union[str, pygame.Color, Tuple[int, int, int]] = "white", highlight: Tuple[int, int, int, int] = (0, 0, 0, 128), 
                 font: Union[pygame.font.SysFont, pygame.font.Font] = None, encoding: str = "utf-8", offset: int = 50,
                 delay: float = 0, youtube: bool = False, pref_lang: str = "en") -> None:
        
        self.path = path
        self.encoding = encoding

        self.youtube = youtube
        self.pref_lang = pref_lang
        self._auto_cap = False
        self.buffer = ""
        if youtube:
            if YTDLP:
                self.buffer = self._extract_youtube_subs(path, pref_lang)
            else:
                raise ModuleNotFoundError("Unable to fetch subtitles because YTDLP is not installed. YTDLP can be installed via pip.")
        elif self._is_video():
            self.buffer = self._extract_internal_subs(path, 0, encoding, "ass")

        self._subs = self._load()

        self.start = 0
        self.end = 0
        self.text = ""
        self.surf = pygame.Surface((0, 0))
        self.offset = offset
        self.delay = delay

        self.colour = colour
        self.highlight = highlight 

        self.font = pygame.font.SysFont("arial", 30) if font is None else font

    def __str__(self):
        return f"<Subtitles(path={self.path})>"

    def _is_video(self):
        return self.path.endswith(".mp4")

    def _load(self):
        if self.youtube or self._is_video():
            return iter(pysubs2.SSAFile.from_string(self.buffer))
        return iter(pysubs2.load(self.path, encoding=self.encoding))

    def _to_surf(self, text):
        h = self.font.get_height()

        lines = text.splitlines()
        surfs = [self.font.render(line, True, self.colour) for line in lines]

        surface = pygame.Surface((max([s.get_width() for s in surfs]), len(surfs) * h), pygame.SRCALPHA)
        surface.fill(self.highlight)
        for i, surf in enumerate(surfs):
            surface.blit(surf, (surface.get_width() / 2 - surf.get_width() / 2, i * h))

        return surface

    def _extract_internal_subs(self, path, index, encoding, f):
        try:
            p = subprocess.Popen(f"ffmpeg -i {path} -loglevel {FFMPEG_LOGLVL} -map 0:s:{index} -f {f} -", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        return p.communicate()[0].decode(encoding)

    def _extract_youtube_subs(self, url, lang):
        cfg = {
            "quiet":True,
            "skip_download": True,
            "writeautomaticsub": True,
            "subtitleslangs": [lang],
            "subtitlesformat": "vtt"
        }

        with yt_dlp.YoutubeDL(cfg) as ydl:
            info = ydl.extract_info(url, download=False)

            subs = info.get("subtitles", {})
            if not lang in subs:                
                subs = info.get("automatic_captions", {})

                self._auto_cap = True

            for i, s in enumerate(subs[lang]):
                if s["ext"] == "vtt":
                    return ydl.urlopen(subs[lang][i]["url"]).read().decode("utf-8")

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

    def get_font(self) -> Union[pygame.font.SysFont, pygame.font.Font]:
        return self.font
