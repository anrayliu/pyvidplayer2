'''
This is an example showing off webcam streaming
'''

import pygame
from pyvidplayer2 import Webcam

# you can change these values to whatever your webcam supports
webcam = Webcam(fps=30, capture_size=(480, 640))

win = pygame.display.set_mode(webcam.current_size)
pygame.display.set_caption("webcam_demo")
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
