'''
This example shows how every video can play subtitles
'''

import pygame
from pyvidplayer2 import Video, Subtitles


win = pygame.display.set_mode((960, 360))
pygame.display.set_caption("parallel subtitles demo")

vid1 = Video(r"resources\trailer1.mp4", subs=Subtitles(r"resources\subs1.srt"))
vid1.resize((480, 360))

vid2 = Video(r"resources\trailer2.mp4", subs=Subtitles(r"resources\subs2.srt"))
vid2.resize((480, 360))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()
    
    pygame.time.wait(16)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (480, 0))

    pygame.display.update()