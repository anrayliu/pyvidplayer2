import pygame
import numpy as np
from typing import Callable, Union, Tuple
from .video import Video, READER_AUTO
from .post_processing import PostProcessing


class VideoPygame(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """
    
    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1, subs: "pyvidplayer2.Subtitles" = None, post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False, no_audio: bool = False, speed: float = 1, youtube: bool = False, max_res: int = 720,
                 as_bytes: bool = False, audio_track: int = 0, vfr: bool = False, pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader)

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), (data.shape[1], data.shape[0]), self._vid._colour_format)
    
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

    def show_subs(self) -> None:
        self.subs_hidden = False
        if self.frame_data is not None:
            self.frame_surf = self._create_frame(self.frame_data)
            if self.subs:
                self._write_subs(self.frame / self.frame_rate)

    def hide_subs(self) -> None:
        self.subs_hidden = True
        if self.frame_data is not None:
            self.frame_surf = self._create_frame(self.frame_data)

    def set_subs(self, subs: "pyvidplayer2.Subtitles") -> None:
        self.subs = self._filter_subs(subs)
