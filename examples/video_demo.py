'''
This is the same example from the original pyvidplayer
The video class still does everything it did, but with many more features
'''


import pygame
from pyvidplayer2 import Video

pygame.init()
win = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# 1. provide video class with the path to your file
vid = Video(r"resources\medic.mov")

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 3. close video when done to release resources
            vid.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    #your program frame rate does not affect video playback
    clock.tick(60)
    
    if key == "r":
        vid.restart()           #rewind video to beginning
    elif key == "p":
        vid.toggle_pause()      #pause/plays video
    elif key == "right":
        vid.seek(15)            #skip 15 seconds in video
    elif key == "left":
        vid.seek(-15)           #rewind 15 seconds in video
    elif key == "up":
        vid.set_volume(1.0)     #max volume
    elif key == "down":
        vid.set_volume(0.0)     #min volume
        
    # 2. draw the video to the given surface, at the given position

    # with force_draw=False, only new frames will be drawn, saving
    # resources by not drawing already existing frames

    vid.draw(win, (0, 0), force_draw=False)
    
    pygame.display.update()
