import cv2
import pygame
from typing import Tuple
from .parallel_video import ParallelVideo
from .post_processing import PostProcessing


class VideoCollection:
    def __init__(self) -> None:
        self.videos = []
        self.positions = []

    def __str__(self) -> str:
        return f"<VideoCollection(count={len(self.videos)})>"

    def add_video(self, path: str, rect: Tuple[int, int, int, int], subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR) -> None:
        pv = None
        for v in self.videos:
            if v.path == path:
                pv = v.copy_sound(subs, post_process, interp)
                break
        if pv is None:
            pv = ParallelVideo(path, subs, post_process, interp)
        pv.resize((rect[2:]))
        pv.stop()

        self.videos.append(pv)
        self.positions.append(rect[:2])

    def play(self) -> None:
        for v in self.videos:
            v.play() 

    def stop(self) -> None:
        for v in self.videos:
            v.stop() 

    def resize(self, pos: Tuple[int, int]) -> None:
        for v in self.videos:
            v.resize(pos) 

    def close(self) -> None:
        for v in self.videos:
            v.close()

    def draw(self, surf: pygame.Surface, force_draw=True) -> None:
        for video, pos in zip(self.videos, self.positions):
            video.draw(surf, pos, force_draw)