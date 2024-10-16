'''
This example shows how VideoPlayers can hold youtube videos 
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

win = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("video player youtube demo")

vid = VideoPlayer(Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=720), (0, 0, 1280, 720), interactable=True)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
    
    pygame.time.wait(16)
    
    win.fill("white")
    
    vid.update(events)
    vid.draw(win)
    
    pygame.display.update()
