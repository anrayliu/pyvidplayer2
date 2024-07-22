'''
This is an example of the built in GUI for videos
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

win = pygame.display.set_mode((1124, 868))
pygame.display.set_caption("video player demo")

vid = VideoPlayer(Video(r"resources\ocean.mkv"), (50, 50, 1024, 768), interactable=True)


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
