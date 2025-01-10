'''
This example shows off preview thumbnails in the video player
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

video = Video(r"resources\medic.mov")

# specify the number of loaded preview_thumbnails during instantiation
# the video will load the specified number of frames before running, and when
# seeking, the closest preloaded frame will be displayed as a preview thumbnail
# therefore, how many frames you choose to load depends on the length of your video,
# how accurate you want the thumbnails to be, and how much you value speed and memory

# Adding preview_thumbnails from the videoplayer is expensive
# In some situations, it may be faster to preload all the frames
# in the video object itself before adding it to the videoplayer,
# which will speed up preview_thumbnails considerably
#
# e.g. video._preload_frames()

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
    
    player.update(events)
    player.draw(win)
    
    pygame.display.update()
