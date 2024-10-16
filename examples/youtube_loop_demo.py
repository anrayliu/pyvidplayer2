'''
This is an example of using and looping Youtube videos with a VideoPlayer
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

v = Video("https://www.youtube.com/watch?v=FihbRSl6wmQ", youtube=True)
player = VideoPlayer(v, (0, 0, *v.current_size), loop=True, interactable=True)

win = pygame.display.set_mode(v.current_size)
pygame.display.set_caption("youtube loop demo")


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            pygame.quit()
            exit()
    
    pygame.time.wait(16)
    
    player.update(events)
    player.draw(win)
    
    pygame.display.update()
