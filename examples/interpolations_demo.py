'''
This example compares the default interpolation technique with the best
Can you tell a difference?
'''

import pygame
from pyvidplayer2 import Video


win = pygame.display.set_mode((1280, 480))
pygame.display.set_caption("interpolations demo")

# default

vid1 = Video(r"resources\medic.mov", interp="linear")
vid1.change_resolution(480)

# best

vid2 = Video(r"resources\medic.mov", interp="lanczos4")
vid2.change_resolution(480)


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