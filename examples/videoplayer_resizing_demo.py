'''
This example shows the resizing features of the VideoPlayer object
Drag and resize the window to see
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

v = Video(r"resources\medic.mov")
player = VideoPlayer(v, (0, 0, *v.current_size))

win = pygame.display.set_mode(v.current_size, pygame.RESIZABLE)
pygame.display.set_caption("video player resizing demo")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.toggle_zoom()
        elif event.type == pygame.VIDEORESIZE:
            player.resize(win.get_size())
    
    pygame.time.wait(16)
    
    win.fill("white")
    
    player.update(events)
    player.draw(win)
    
    pygame.display.update()
