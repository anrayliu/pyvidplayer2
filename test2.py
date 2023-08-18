import pygame
from pyvidplayer2 import Webcam

pygame.init()
win = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

#provide video class with the path to your video
vid = Webcam(0)

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    #your program frame rate does not affect video playback
    clock.tick(60)
    
    #draws the video to the given surface, at the given position
    vid.draw(win, (0, 0), force_draw=False)
    
    pygame.display.update()