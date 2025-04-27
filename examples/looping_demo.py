'''
This is an example of seamless looping

v0.9.26 brought significant improvements to looping
looping is now much more seamless
'''

# Sample videos can be found here: https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import VideoPlayer, Video

v = Video(r"resources\clip.mp4")
player = VideoPlayer(v, (0, 0, *v.current_size), loop=True)

win = pygame.display.set_mode(v.current_size)
pygame.display.set_caption("looping demo")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.video.restart()
    
    pygame.time.wait(16)
    
    player.update(events)
    player.draw(win)

    pygame.display.update()
