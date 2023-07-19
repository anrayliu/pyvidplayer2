import pygame
import cv2 
import math
from typing import Tuple, List
from .post_processing import PostProcessing
from .video import Video



class VideoPlayer:
    def __init__(self, path, rect, interactable=True, loop=False, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR) -> None:

        self.vid = Video(path, chunk_size, max_threads, max_chunks, subs, post_process, interp)
        self.frame_rect = pygame.Rect(rect)
        self.interactable = interactable
        self.loop = loop 

        self.vid_rect = pygame.Rect(0, 0, 0, 0)
        self._progress_back = pygame.Rect(0, 0, 0, 0)
        self._progress_bar = pygame.Rect(0, 0, 0, 0)
        self._font = pygame.font.SysFont("arial", 0)

        self._buffer_rect = pygame.Rect(0, 0, 0, 0)
        self._buffer_angle = 0

        self._transform(self.frame_rect)

        self._show_ui = False
        self.queue_ = []

        self._clock = pygame.time.Clock()
        
        self._seek_pos = 0 
        self._seek_time = 0
        self._show_seek = False

    def __str__(self) -> str:
        return f"<VideoPlayer(path={self.path})>"

    def _best_fit(self, rect: pygame.Rect, r: float) -> pygame.Rect:
        s = rect.size
        r = self.vid.aspect_ratio
        
        w = s[0]
        h = int(w / r)
        y = int(s[1] /2 - h / 2)
        x = 0
        if h > s[1]:
            h = s[1]
            w = int(h * r)
            x = int(s[0] / 2 - w / 2)
            y = 0
            
        return pygame.Rect(rect.x + x, rect.y + y, w, h)

    def _transform(self, rect: pygame.Rect) -> None:
        self.frame_rect = rect
        self.vid_rect = self._best_fit(self.frame_rect, self.vid.aspect_ratio)
        self.vid.resize(self.vid_rect.size)

        self._progress_back = pygame.Rect(self.frame_rect.x + 10, self.frame_rect.bottom - 25, self.frame_rect.w - 20, 15)
        self._progress_bar = self._progress_back.copy()

        self._font = pygame.font.SysFont("arial", 10)

        if self.vid.frame_data is not None:
            self.vid.frame_surf = pygame.transform.smoothscale(self.vid.frame_surf, self.vid_rect.size)

        self._buffer_rect = pygame.Rect(0, 0, 200, 200)
        self._buffer_rect.center = self.frame_rect.center

    def _move_angle(self, pos: Tuple[int, int], angle: float, distance: int) -> Tuple[float, float]:
        return pos[0] + math.cos(angle) * distance, pos[1] + math.sin(angle) * distance
    
    def _convert_seconds(self, time: float) -> str:
        return self.vid._convert_seconds(time).split(".")[0]
    
    def zoom_to_fill(self):
        s = max(abs(self.frame_rect.w - self.vid_rect.w), abs(self.frame_rect.h - self.vid_rect.h))
        self.vid_rect.inflate_ip(s, s)
        self.vid.resize(self.vid_rect.size)
        self.vid_rect.center = self.frame_rect.center

    def zoom_out(self):
        self.vid_rect = self._best_fit(self.frame_rect, self.vid.aspect_ratio)
        self.vid.resize(self.vid_rect.size)

    def queue(self, path: str) -> None:
        self.queue_.append(path)

    def resize(self, size: Tuple[int, int]) -> None:
        self.frame_rect.size = size
        self._transform(self.frame_rect)

    def move(self, pos: Tuple[int, int], relative=False) -> None:
        if relative:
            self.frame_rect.move_ip(*pos)
        else:
            self.frame_rect.topleft = pos
        self._transform(self.frame_rect)

    def update(self, events: List[pygame.event.Event] = None, show_ui=None) -> None:
        if self.vid._update() and self.vid.current_size > self.frame_rect.size:
            self.vid.frame_surf = self.vid.frame_surf.subsurface(self.frame_rect.x - self.vid_rect.x, self.frame_rect.y - self.vid_rect.y, *self.frame_rect.size)

        if self.interactable:

            mouse = pygame.mouse.get_pos()
            click = False 
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True 

            self._show_ui = self.frame_rect.collidepoint(mouse) if show_ui is None else show_ui

            if self._show_ui:
                self._progress_bar.w = self._progress_back.w * (self.vid.get_pos() / self.vid.duration)

                self._show_seek = self._progress_back.collidepoint(mouse)

                if self._show_seek:
                    t = (self._progress_back.w - (self._progress_back.right - mouse[0])) * (self.vid.duration / self._progress_back.w)

                    self._seek_pos = self._progress_back.w * (round(t, 1) / self.vid.duration) + self._progress_back.x
                    self._seek_time = t

                    if click:
                        self.vid.seek(t, relative=False)
                        self.vid.play()
                
                elif click:
                    self.vid.toggle_pause()

        if not self.vid.active:
            if self.queue_:
                if self.loop:
                    self.queue_.append(self.vid.path)
                self.vid = Video(self.queue_.pop(0))
                self._transform(self.frame_rect)
            elif self.loop:
                self.vid.restart()

        self._buffer_angle += self._clock.tick() / 10

    def draw(self, win: pygame.Surface) -> None:
        pygame.draw.rect(win, "black", self.frame_rect)
        if self.vid.frame_surf is not None:
            win.blit(self.vid.frame_surf, self.frame_rect.topleft if self.vid.current_size > self.frame_rect.size else self.vid_rect.topleft)

        if self._show_ui:
            pygame.draw.line(win, (50, 50, 50), (self._progress_back.x, self._progress_back.centery), (self._progress_back.right, self._progress_back.centery), 5)
            if self._progress_bar.w > 0:
                pygame.draw.line(win, "white", (self._progress_bar.x, self._progress_bar.centery), (self._progress_bar.right, self._progress_bar.centery), 5)

            f = self._font.render(self.vid.name, True, "white")
            win.blit(f, (self.frame_rect.x + 10, self.frame_rect.y + 10))

            f = self._font.render(self._convert_seconds(self.vid.get_pos()), True, "white")
            win.blit(f, (self.frame_rect.x + 10, self._progress_bar.top - f.get_height() - 10))

            if self._show_seek:
                pygame.draw.line(win, "white", (self._seek_pos, self._progress_back.top), (self._seek_pos, self._progress_back.bottom), 2)
                
                f = self._font.render(self._convert_seconds(self._seek_time), True, "white")
                win.blit(f, (self._seek_pos - f.get_width() // 2, self._progress_back.y - 10 - f.get_height()))

        if self.interactable:
            if self.vid.buffering:
                for i in range(6):
                    a = math.radians(self._buffer_angle + i * 60)
                    pygame.draw.line(win, "white", self._move_angle(self.frame_rect.center, a, 10), self._move_angle(self.frame_rect.center, a, 30))
            elif self.vid.paused:
                pygame.draw.rect(win, "white", (self.frame_rect.centerx - 15, self.frame_rect.centery - 20, 10, 40))
                pygame.draw.rect(win, "white", (self.frame_rect.centerx + 5, self.frame_rect.centery - 20, 10, 40))

    def close(self) -> None:
        self.vid.close()