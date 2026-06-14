'''
This example compares area and lanczos4 interpolation in slow motion
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import Video


win = pygame.display.set_mode((1708, 480))
pygame.display.set_caption("interpolations demo")

PATH = "resources/trailer1.mp4"

# if you change this to the default "linear" technique, you'll notice that
# it's almost indistinguishable from lanczos4 at low resolutions

vid1 = Video(PATH, interp="area")
# automatically resizes video to maintain aspect ratio
vid1.change_resolution(2160)

# sharpest but least performant interpolation technique
vid2 = Video(PATH, interp="lanczos4")
vid2.change_resolution(2160)

# can also switch interpolation technique with this method
vid2.set_interp("lanczos4")

# arbitrary frame
vid1.seek_frame(1000)
vid2.seek_frame(1000)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()

    pygame.time.wait(16)

    win.blit(vid1.frame_surf.subsurface(0, 300, 854, 480), (0, 0))
    win.blit(vid2.frame_surf.subsurface(0, 300, 854, 480), (854, 0))

    pygame.display.update()
