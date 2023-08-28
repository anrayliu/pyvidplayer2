import pygame 
import pysubs2


class Subtitles:
    def __init__(self, path: str, colour="white", highlight=(0, 0, 0, 128), font=pygame.font.SysFont("arial", 30), encoding="utf-8", offset=50) -> None:
        self.path = path
        self.encoding = encoding

        self._subs = iter(pysubs2.load(path, encoding=encoding))

        self.start = 0
        self.end = 0
        self.text = ""
        self.surf = pygame.Surface((0, 0))
        self.offset = offset

        self.colour = colour
        self.highlight = highlight 
        self.font = font

    def __str__(self) -> str:
        return f"<Subtitles(path={self.path})>"

    def _to_surf(self, text: str) -> pygame.Surface:
        h = self.font.render(" ", True, "black").get_height()

        lines = text.strip().split("\n")
        surfs = [self.font.render(line, True, self.colour) for line in lines]

        surface = pygame.Surface((max([s.get_width() for s in surfs]), len(surfs) * h), pygame.SRCALPHA)
        surface.fill(self.highlight)
        for i, surf in enumerate(surfs):
            surface.blit(surf, (surface.get_width() / 2 - surf.get_width() / 2, i * h))

        return surface
    
    def _get_next(self) -> bool:
        try:
            s = next(self._subs)
        except StopIteration:
            self.start = 0
            self.end = 0
            self.text = ""
            self.surf = pygame.Surface((0, 0))
            return False 
        else:
            self.start = s.start / 1000
            self.end = s.end / 1000
            self.text = s.plaintext
            self.surf = self._to_surf(self.text)
            return True

    def _seek(self, time: float) -> None:
        self._subs = iter(pysubs2.load(self.path, encoding=self.encoding))

        while not (self.start <= time <= self.end):
            if not self._get_next():
                break

    def _write_subs(self, surf: pygame.Surface) -> None:
        surf.blit(self.surf, (surf.get_width() / 2 - self.surf.get_width() / 2, surf.get_height() - self.surf.get_height() - self.offset))
        
    def set_font(self, font: pygame.font.SysFont) -> None:
        self.font = font

    def get_font(self) -> pygame.font.SysFont:
        return self.font
