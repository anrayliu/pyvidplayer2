'''
This is an example of the built in GUI for videos
'''


import pygame
from pyvidplayer2 import VideoPlayer, Video

video = Video(r"resources\ocean.mkv")

win = pygame.display.set_mode(video.original_size, pygame.RESIZABLE)
pygame.display.set_caption("video player demo")

# 1. create video player with a video object and a space on screen
player = VideoPlayer(video, (0, 0, *video.original_size), interactable=True)

# can also take youtube videos
# player = VideoPlayer(Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True, max_res=720), (0, 0, 1280, 720), interactable=True)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            # 4. close when done, also closing the video inside
            player.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # can toggle between zoom to fill and whole video
            player.toggle_zoom()
        elif event.type == pygame.VIDEORESIZE:
            # vide player will always ensure that none of the video is cut off after resizing
            player.resize(win.get_size())

    pygame.time.wait(16)
    
    win.fill("white")

    # 2. update video player with events list
    player.update(events)
    # 3. draw video player
    player.draw(win)
    
    pygame.display.update()
