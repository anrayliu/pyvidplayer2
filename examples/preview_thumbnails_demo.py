'''
This example shows off preview thumbnails in the video player
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

video = Video(r"resources\medic.mov")
player = VideoPlayer(video, (0, 0, *video.original_size), interactable=True, preview_thumbnails=100)

win = pygame.display.set_mode(video.original_size)
pygame.display.set_caption("preview thumbnails demo")


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            pygame.quit()
            exit()
    
    pygame.time.wait(16)
    
    win.fill("white")
    
    player.update(events)
    player.draw(win)
    
    pygame.display.update()
