import pygame
from pyvidplayer2 import VideoCollection, PostProcessing

PATH = r"resources\trailer.mp4"

win = pygame.display.set_mode((960, 240))
pygame.display.set_caption("post processing demo")
clock = pygame.time.Clock()

# using a video collection to play videos in parallel for a side to side comparison

video = VideoCollection()

video.add_video(PATH, (0, 0, 320, 240), post_process=PostProcessing.sharpen)
video.add_video(PATH, (320, 0, 320, 240))
video.add_video(PATH, (640, 0, 320, 240), post_process=PostProcessing.blur)

video.play()

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            video.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    clock.tick(60)
        
    video.draw(win)

    pygame.display.update()