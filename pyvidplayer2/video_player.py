import pygame
import math
from typing import Tuple, Union, List
from . import Video
from .error import *
from .video_pygame import VideoPygame


class VideoPlayer:
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """

    def __init__(self, video: Video, rect: Tuple[int, int, int, int], interactable: bool = False, loop: bool = False, preview_thumbnails: int = 0, font_size: int = 10):
        self.video = video
        if isinstance(self.video, VideoPygame):
            if self.video.closed:
                raise VideoStreamError("Provided video is closed.")
        else:
            raise ValueError("Must be a VideoPygame object.")

        self.frame_rect = pygame.Rect(rect)
        self.interactable = interactable
        self.loop = loop
        self.preview_thumbnails = min(max(preview_thumbnails, 0), self.video.frame_count)
        self._show_intervals = self.preview_thumbnails != 0

        self.vid_rect = pygame.Rect(0, 0, 0, 0)
        self._progress_back = pygame.Rect(0, 0, 0, 0)
        self._progress_bar = pygame.Rect(0, 0, 0, 0)
        self._smooth_bar = 0 # used for making the progress bar look smooth when seeking
        self._font = pygame.font.SysFont("arial", font_size)

        self._buffer_rect = pygame.Rect(0, 0, 0, 0)
        self._buffer_angle = 0

        self._zoomed = False

        self._transform(self.frame_rect)

        self._show_ui = False
        self.queue_ = []

        self._clock = pygame.time.Clock()
        
        self._seek_pos = 0 
        self._seek_time = 0
        self._show_seek = False

        self._fade_timer = 0
        
        if self._show_intervals:
            self._interval = self.video.duration / self.preview_thumbnails
            self._interval_frames = []
            self._get_interval_frames()

        self.closed = False

    def __str__(self):
        return f"<VideoPlayer(path={self.video.path})>"

    def __len__(self):
        return len(self.queue_) + 1

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def _close_queue(self):
        for video in self.queue_:
            try:
                video.close()
            except AttributeError:
                pass
    
    def _get_interval_frames(self):
        size = (int(70 * self.video.aspect_ratio), 70)

        self._interval_frames.clear()
        frame = self.video._vid.frame

        for i in range(self.preview_thumbnails):
            if self.video._preloaded:
                data = self.video._preloaded_frames[int(i * self.video.frame_rate * self._interval)]
            else:
                self.video._vid.seek(int(i * self.video.frame_rate * self._interval))
                data = self.video._vid.read()[1]

            self._interval_frames.append(pygame.image.frombuffer(self.video._resize_frame(data, size, "fast_bilinear", True).tobytes(), size, self.video._vid._colour_format))

        # add last readable frame

        if self.video._preloaded:
            self._interval_frames.append(pygame.image.frombuffer(self.video._resize_frame(self.video._preloaded_frames[-1], size, "fast_bilinear", True).tobytes(), size, self.video._vid._colour_format))
        else:
            i = 1
            while True:
                self.video._vid.seek(self.video.frame_count - i)
                try:
                    self._interval_frames.append(pygame.image.frombuffer(self.video._resize_frame(self.video._vid.read()[1], size, "fast_bilinear", True).tobytes(), size, self.video._vid._colour_format))
                except:
                    i += 1
                else:
                    break

            self.video._vid.seek(frame)
    
    def _get_closest_frame(self, time):
        return self._interval_frames[round(time / self._interval)]

    def _transform(self, rect):
        self.frame_rect = rect
        self.zoom_out()

        self._progress_back = pygame.Rect(self.frame_rect.x + 10, self.frame_rect.bottom - 25, self.frame_rect.w - 20, 15)
        self._progress_bar = self._progress_back.copy()

        self._buffer_rect = pygame.Rect(0, 0, 200, 200)
        self._buffer_rect.center = self.frame_rect.center

    def _move_angle(self, pos, angle, distance):
        return pos[0] + math.cos(angle) * distance, pos[1] + math.sin(angle) * distance
    
    def _convert_seconds(self, time):
        return self.video._convert_seconds(time).split(".")[0]
    
    # takes a rect and an aspect ratio, returns the largest rect of the aspect ratio that can be fit inside
    
    def _best_fit(self, rect, r):
        s = rect.size

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

    # called after a video is finished playing
    def _handle_on_end(self):
        if self.queue_:
            if self.loop:
                self.queue(self.video)
            else:
                self.video.close()
            input_ = self.queue_.pop(0)
            if isinstance(input_, Video):
                self.video = input_
                self.video.play()
            else:
                self.video = Video(input_)
            self._transform(self.frame_rect)
        elif self.loop:
            self.video.restart()

    def zoom_to_fill(self) -> None:
        s = max(abs(self.frame_rect.w - self.vid_rect.w), abs(self.frame_rect.h - self.vid_rect.h))
        self.vid_rect.inflate_ip(s, s)
        self.vid_rect.center = self.frame_rect.center #adjusts for 1.0 rounding imprecisions
        self.video.resize(self.vid_rect.size)
        self._zoomed = True

    def zoom_out(self) -> None:
        self.vid_rect = self._best_fit(self.frame_rect, self.video.aspect_ratio)
        self.vid_rect.center = self.frame_rect.center #adjusts for 1.0 rounding imprecisions
        self.video.resize(self.vid_rect.size)
        self._zoomed = False

    def toggle_zoom(self) -> None:
        if self._zoomed:
            self.zoom_out()
        else:
            self.zoom_to_fill()

    def queue(self, input_: Union[str, Video]) -> None:
        self.queue_.append(input_)

        # update once to trigger audio loading
        try:
            input_.stop()
            input_._update()
        except AttributeError:
            pass
        
    def resize(self, size: Tuple[int, int]) -> None:
        self.frame_rect.size = size
        self._transform(self.frame_rect)

    def move(self, pos: Tuple[int, int], relative: bool = False) -> None:
        if relative:
            self.frame_rect.move_ip(*pos)
        else:
            self.frame_rect.topleft = pos
        self._transform(self.frame_rect)

    def update(self, events: List[pygame.event.Event] = None, show_ui: bool = None, fps: int = 0) -> bool:
        dt = self._clock.tick(fps)

        if not self.video.active:
            self._handle_on_end()

        self.video.update()

        if self.interactable:

            mouse = pygame.mouse.get_pos()
            click = False 
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

            self._show_ui = self.frame_rect.collidepoint(mouse) if show_ui is None else show_ui

            if self._show_ui:
                self._progress_bar.w = self._progress_back.w * (self.video.get_pos() / self.video.duration)
                self._smooth_bar += (self._progress_bar.w - self._smooth_bar) * (dt / 100)
                self._show_seek = self._progress_back.collidepoint(mouse)

                if self._show_seek:
                    t = (self._progress_back.w - (self._progress_back.right - mouse[0])) * (self.video.duration / self._progress_back.w)

                    self._seek_pos = self._progress_back.w * (round(t, 1) / self.video.duration) + self._progress_back.x
                    self._seek_time = t

                    if click:
                        self.video.seek(t, relative=False)
                        self.video.play()
                        self._clock.tick()   # resets delta time

                elif click:
                    self.video.toggle_pause()

        self._buffer_angle += dt / 10

        return self._show_ui

    def draw(self, win: pygame.Surface) -> None:
        pygame.draw.rect(win, "black", self.frame_rect)
        buffer = self.video.frame_surf
        if buffer is not None:
            if self._zoomed:
                win.blit(buffer, self.frame_rect.topleft, (self.frame_rect.x - self.vid_rect.x, self.frame_rect.y - self.vid_rect.y, *self.frame_rect.size))
            else:
                win.blit(buffer, self.vid_rect.topleft)

        if self._show_ui:
            pygame.draw.line(win, (50, 50, 50), (self._progress_back.x, self._progress_back.centery), (self._progress_back.right, self._progress_back.centery), 5)
            if self._smooth_bar > 1:
                pygame.draw.line(win, "white", (self._progress_bar.x, self._progress_bar.centery), (self._progress_bar.x + self._smooth_bar, self._progress_bar.centery), 5)

            f = self._font.render(self.video.name, True, "white")
            win.blit(f, (self.frame_rect.x + 10, self.frame_rect.y + 10))

            f = self._font.render(self._convert_seconds(self.video.get_pos()), True, "white")
            win.blit(f, (self.frame_rect.x + 10, self._progress_bar.top - f.get_height() - 10))

            if self._show_seek:
                pygame.draw.line(win, "white", (self._seek_pos, self._progress_back.top), (self._seek_pos, self._progress_back.bottom), 2)

                f = self._font.render(self._convert_seconds(self._seek_time), True, "white")
                win.blit(f, (self._seek_pos - f.get_width() // 2, self._progress_back.y - 10 - f.get_height()))

                if self._show_intervals:
                    surf = self._get_closest_frame(self._seek_time)
                    x = self._seek_pos - surf.get_width() // 2
                    x = min(max(x, self.frame_rect.x), self.frame_rect.right - surf.get_width())
                    pygame.draw.rect(win, (0, 0, 0), (x - 2, self._progress_back.y - 80 - f.get_height() - 2, surf.get_width() + 4, surf.get_height() + 4), 2)
                    win.blit(surf, (x, self._progress_back.y - 80 - f.get_height()))

        if self.interactable:
            if self.video.buffering:
                for i in range(6):
                    a = math.radians(self._buffer_angle + i * 60)
                    pygame.draw.line(win, "white", self._move_angle(self.frame_rect.center, a, 10), self._move_angle(self.frame_rect.center, a, 30))
            elif self.video.paused:
                pygame.draw.rect(win, "white", (self.frame_rect.centerx - 15, self.frame_rect.centery - 20, 10, 40))
                pygame.draw.rect(win, "white", (self.frame_rect.centerx + 5, self.frame_rect.centery - 20, 10, 40))

    def close(self) -> None:
        self.video.close()
        self._close_queue()
        self.closed = True
        
    def skip(self) -> None:
        if self.queue_:
            self.video.stop() if self.loop else self.video.close()
            self._handle_on_end()

    def get_next(self) -> Union[str, Video]:
        return self.queue_[0] if self.queue_ else None
    
    def clear_queue(self) -> None:
        self._close_queue()
        self.queue_.clear()

    def get_video(self) -> Video:
        return self.video
    
    def get_queue(self) -> List[Union[str, Video]]:
        return self.queue_

    def preview(self, max_fps: int = 60):
        win = pygame.display.set_mode(self.frame_rect.size, pygame.RESIZABLE)
        pygame.display.set_caption(f"videoplayer - {self.video.name}")
        self.video.play()
        while self.video.active:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.video.stop()
                elif event.type == pygame.WINDOWRESIZED:
                    self.resize(win.get_size())
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.toggle_zoom()
            self.update(events, True, max_fps)
            self.draw(win)
            pygame.display.update()
        pygame.display.quit()
        self.close()