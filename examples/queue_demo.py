'''
This example shows how videos can be queued and skipped through with the VideoPlayer object
'''

import pygame
from pyvidplayer2 import VideoPlayer, Video

win = pygame.display.set_mode((1280, 720))


vid = VideoPlayer(Video(r"resources\ocean.mkv"), (0, 0, 1280, 720), loop=True)

vid.queue(Video(r"resources\billiejean.mp4"))
vid.queue(Video(r"resources\birds.avi"))


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            vid.close_all()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            vid.skip()
    
    pygame.time.wait(16)
    
    win.fill("white")
    
    vid.update(events)
    vid.draw(win)
    
    pygame.display.update()