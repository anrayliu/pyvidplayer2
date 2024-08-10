import cv2
import time
import pygame 
from .video import Video
from .post_processing import PostProcessing


class VideoPygame(Video):
    def __init__(self, path, chunk_size=10, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=False, reverse=False, no_audio=False, speed=1, youtube=False, max_res=1080):
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res)

    def __str__(self):
        return f"<VideoPygame(path={self.path})>"

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf, pos):
        surf.blit(self.frame_surf, pos)
    
    def preview(self, show_fps=False):
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
            dt = clock.tick(self.frame_rate * 2)
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
