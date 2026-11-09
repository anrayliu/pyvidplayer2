'''
This is an example of playing many videos at once
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import Video, VideoPlayer

win = pygame.display.set_mode((1066, 744))
pygame.display.set_caption("many videos demo")

# simultaneous playback is only possible when using Sounddevice for audio

videos = [VideoPlayer(Video("resources/billiejean.mp4"), (0, 0, 426, 240)),
          VideoPlayer(Video("resources/trailer1.mp4"), (426, 0, 256, 144)),
          VideoPlayer(Video("resources/medic.mov"), (682, 0, 256, 144)),
          VideoPlayer(Video("resources/trailer2.mp4"), (426, 144, 640, 360)),
          VideoPlayer(Video("resources/clip.mp4"), (0, 240, 256, 144)),
          VideoPlayer(Video("resources/birds.avi"), (0, 384, 426, 240)),
          VideoPlayer(Video("resources/ocean.mkv"), (426, 504, 426, 240))]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            [video.close() for video in videos]
            pygame.quit()
            exit()

    pygame.time.wait(16)

    win.fill("white")

    [video.update() for video in videos]
    [video.draw(win) for video in videos]

    pygame.display.update()
