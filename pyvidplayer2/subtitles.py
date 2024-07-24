import pygame 
import pysubs2


class Subtitles:
    def __init__(self, path, colour="white", highlight=(0, 0, 0, 128), font=pygame.font.SysFont("arial", 30), encoding="utf-8", offset=50):
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

    def __str__(self):
        return f"<Subtitles(path={self.path})>"

    def _to_surf(self, text):
        h = self.font.get_height()

        lines = text.strip().split("\n")
        surfs = [self.font.render(line, True, self.colour) for line in lines]

        surface = pygame.Surface((max([s.get_width() for s in surfs]), len(surfs) * h), pygame.SRCALPHA)
        surface.fill(self.highlight)
        for i, surf in enumerate(surfs):
            surface.blit(surf, (surface.get_width() / 2 - surf.get_width() / 2, i * h))

        return surface
    
    def _get_next(self):
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

    def _seek(self, time):
        self._subs = iter(pysubs2.load(self.path, encoding=self.encoding))

        self.end = 0
        self.start = 0
        self.text = ""
        self.surf = pygame.Surface((0, 0))

        while self.end < time:
            if not self._get_next():
                break

    def _write_subs(self, surf):
        surf.blit(self.surf, (surf.get_width() / 2 - self.surf.get_width() / 2, surf.get_height() - self.surf.get_height() - self.offset))
        
    def set_font(self, font):
        self.font = font

    def get_font(self):
        return self.font
