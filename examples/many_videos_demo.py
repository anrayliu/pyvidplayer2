'''
This is an example of playing many videos at once
'''


import pygame
from pyvidplayer2 import Video, VideoPlayer

win = pygame.display.set_mode((1066, 744))
pygame.display.set_caption("many videos demo")

# simultaneous playback is only possible when using PyAudio for audio

videos = [VideoPlayer(Video(r"resources\billiejean.mp4"), (0, 0, 426, 240),),
          VideoPlayer(Video(r"resources\trailer1.mp4"), (426, 0, 256, 144)),
          VideoPlayer(Video(r"resources\medic.mov"), (682, 0, 256, 144)),
          VideoPlayer(Video(r"resources\trailer2.mp4"), (426, 144, 640, 360)),
          VideoPlayer(Video(r"resources\clip.mp4"), (0, 240, 256, 144)),
          VideoPlayer(Video(r"resources\birds.avi"), (0, 384, 426, 240)),
          VideoPlayer(Video(r"resources\ocean.mkv"), (426, 504, 426, 240))]

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            [video.close() for video in videos]
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    pygame.time.wait(16)
    
    win.fill("white")
    
    [video.update() for video in videos]
    [video.draw(win) for video in videos]

    pygame.display.update()