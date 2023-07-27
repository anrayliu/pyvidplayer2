'''
This is an example of the built in GUI for videos
'''


import pygame
from pyvidplayer2 import VideoPlayer

win = pygame.display.set_mode((1124, 868))
pygame.display.set_caption("video player demo")
clock = pygame.time.Clock()

vid = VideoPlayer(r"resources\trailer2.mp4", (50, 50, 1024, 768))


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
    
    clock.tick(60)
    
    win.fill("white")
    
    vid.update(events)
    vid.draw(win)
    
    pygame.display.update()
