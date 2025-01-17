'''
This example compares the default interpolation technique with the best
Can you tell a difference?
'''

import pygame
from pyvidplayer2 import Video


win = pygame.display.set_mode((1280, 480))
pygame.display.set_caption("interpolations demo")

# default interpolation technique

vid1 = Video(r"resources\medic.mov", interp="linear")
vid1.change_resolution(480) # automatically resizes video to maintain aspect ratio

# sharpest but least performant interpolation technique

vid2 = Video(r"resources\medic.mov", interp="lanczos4")
vid2.resize((854, 480)) # alternatively, can set a custom size


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()
    
    pygame.time.wait(16)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (640, 0))

    pygame.display.update()
