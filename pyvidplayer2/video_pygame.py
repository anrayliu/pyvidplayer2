import cv2 
import pygame 
from .video import Video
from .post_processing import PostProcessing


class VideoPygame(Video):
    def __init__(self, path, chunk_size=10, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, use_pygame_audio=False, reverse=False, no_audio=False, speed=1):
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, subs, post_process, interp, use_pygame_audio, reverse, no_audio, speed)

    def __str__(self):
        return f"<VideoPygame(path={self.path})>"

    def _create_frame(self, data):
        return pygame.image.frombuffer(data.tobytes(), self.current_size, "BGR")
    
    def _render_frame(self, surf, pos):
        surf.blit(self.frame_surf, pos)
    
    def preview(self):
        win = pygame.display.set_mode(self.current_size)
        pygame.display.set_caption(f"pygame - {self.name}")
        self.play()
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
            pygame.time.wait(16)
            self.draw(win, (0, 0), force_draw=False)
            pygame.display.update()
        pygame.display.quit()
        self.close()
