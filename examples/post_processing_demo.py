'''
This example gives a side by side comparison between a few available post process effects
'''


import pygame
from pyvidplayer2 import VideoCollection, PostProcessing

PATH = r"resources\trailer2.mp4"

win = pygame.display.set_mode((960, 240))
pygame.display.set_caption("post processing demo")
clock = pygame.time.Clock()

# using a video collection to play videos in parallel for a side to side comparison

video = VideoCollection()

video.add_video(PATH, (0, 0, 320, 240), post_process=PostProcessing.sharpen)
video.add_video(PATH, (320, 0, 320, 240))
video.add_video(PATH, (640, 0, 320, 240), post_process=PostProcessing.blur)

video.play()

font = pygame.font.SysFont("arial", 30)
surfs = [font.render("Sharpen", True, "white"), font.render("Normal", True, "white"), font.render("Blur", True, "white")]


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
    
    for i, surf in enumerate(surfs):
        pygame.draw.rect(win, "black", (320 * i, 0, *surf.get_size()))
        win.blit(surf, (320 * i, 0))

    pygame.display.update()