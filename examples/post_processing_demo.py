'''
This example gives a side by side comparison between a few available post process effects
'''


import pygame
from pyvidplayer2 import Video, PostProcessing

PATH = r"resources\ocean.mkv"

win = pygame.display.set_mode((960, 240))
pygame.display.set_caption("post processing demo")

# supply a post processing function here
# you can use provided ones from the PostProcessing class, or you can make your own
# all post processing functions must accept and return a numpy ndarray
# post processing functions are applied to each frame before rendering
# both the frame_data and frame_surf properties have post processing applied to them

def custom_post_processing(data):
    return data     # do nothing with the frame

videos = [Video(PATH, post_process=PostProcessing.sharpen),
          Video(PATH, post_process=custom_post_processing),
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
