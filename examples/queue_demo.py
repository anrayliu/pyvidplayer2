'''
This example shows how videos can be queued and skipped through with the VideoPlayer object
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import Video, VideoPlayer

win = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("queue demo")

# with loop=True and videos in the queue, each video will be added
# back into the queue after it finishes playing

player = VideoPlayer(Video(r"resources\clip.mp4"), (0, 0, 1280, 720), loop=True)

# queue video objects
# when the current video finishes playing, the next video will automatically start
player.queue(Video(r"resources\ocean.mkv"))
player.queue(Video(r"resources\birds.avi"))
# can also queue video paths to prevent resources from loading before needed
player.queue("resources/trailer2.mp4")

# you can also access the list of queued videos with the following
# note that this list does not include the currently loaded video in the player
player.get_queue()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            player.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # skips a video in the queue
            player.skip()

    pygame.time.wait(16)

    player.update(events)
    player.draw(win)

    pygame.display.update()
