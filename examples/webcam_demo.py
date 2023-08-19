'''
Webcam example
'''

import pygame
from pyvidplayer2 import Webcam

webcam = Webcam()

win = pygame.display.set_mode(webcam.current_size)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            webcam.close()
            pygame.quit()
            exit()
    
    clock.tick(60)
    
    webcam.draw(win, (0, 0), force_draw=False)
    
    pygame.display.update()