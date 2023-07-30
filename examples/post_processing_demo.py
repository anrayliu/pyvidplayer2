'''
This example gives a side by side comparison between a few available post process effects
'''


import pygame
from pyvidplayer2 import Video, PostProcessing

PATH = r"resources\ocean.mkv"

win = pygame.display.set_mode((960, 240))
pygame.display.set_caption("post processing demo")

# using a video collection to play videos in parallel for a side to side comparison

videos = [Video(PATH, post_process=PostProcessing.sharpen),
          Video(PATH),
          Video(PATH, post_process=PostProcessing.blur)]

font = pygame.font.SysFont("arial", 30)
surfs = [font.render("Sharpen", True, "white"), font.render("Normal", True, "white"), font.render("Blur", True, "white")]


while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            [video.close() for video in videos]
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    pygame.time.wait(16)
        
    for i, surf in enumerate(surfs):
        x = 320 * i
        videos[i].draw(win, (x, 0))
        pygame.draw.rect(win, "black", (x, 0, *surf.get_size()))
        win.blit(surf, (x, 0))

    pygame.display.update()