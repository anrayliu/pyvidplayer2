'''
This example shows how subtitles can be delayed by a global value
Useful if your subtitle file is slightly misaligned
'''


import pygame 
from pyvidplayer2 import Video, VideoPlayer, Subtitles


DELAY = -1.0       # in seconds


video = Video("resources\\trailer1.mp4", subs=Subtitles("resources\\subs1.srt", delay=DELAY))
player = VideoPlayer(video, (0, 0, *video.original_size), interactable=True)

win = pygame.display.set_mode(video.original_size)
pygame.display.set_caption("")


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            quit()

    player.update(events, fps=0)
    player.draw(win)

    pygame.display.update()
