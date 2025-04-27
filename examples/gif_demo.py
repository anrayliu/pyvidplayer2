'''
This is an example of playing gifs

Gifs are essentially treated as videos with no sound
Uses looping_demo.py to loop the gif
'''

# Sample videos can be found here: https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import VideoPlayer, Video

v = Video("some-gif.gif")
player = VideoPlayer(v, (0, 0, *v.current_size), loop=True)

win = pygame.display.set_mode(v.current_size)
pygame.display.set_caption("gif demo")

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
