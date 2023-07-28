'''
This is an example of two videos playing simultaneously with the ParallelVideo class
If you want to play a large amount of videos in parallel, the VideoCollection class might be helpful
'''

import pygame
from pyvidplayer2 import ParallelVideo


win = pygame.display.set_mode((960, 360))
pygame.display.set_caption("parallel playing demo")

vid1 = ParallelVideo(r"resources\trailer1.mp4")
vid1.resize((480, 360))

vid2 = ParallelVideo(r"resources\trailer2.mp4")
vid2.resize((480, 360))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()

    pygame.time.wait(16)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (480, 0))

    pygame.display.update()