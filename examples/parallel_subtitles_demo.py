'''
This example shows how ParallelVideos can also play subtitles
'''

import pygame
from pyvidplayer2 import ParallelVideo, Subtitles


win = pygame.display.set_mode((960, 360))
pygame.display.set_caption("parallel subtitles demo")
clock = pygame.time.Clock()

vid1 = ParallelVideo(r"resources\trailer1.mp4", subs=Subtitles(r"resources\subs1.srt"))
vid1.resize((480, 360))

vid2 = ParallelVideo(r"resources\trailer2.mp4", subs=Subtitles(r"resources\subs2.srt"))
vid2.resize((480, 360))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()
    
    clock.tick(60)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (480, 0))

    pygame.display.update()