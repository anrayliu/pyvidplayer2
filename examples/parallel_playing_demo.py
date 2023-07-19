import pygame
from pyvidplayer2 import ParallelVideo

PATH1 = "demos\\vids\\vid.mp4"
PATH2 = "demos\\vids\\ep2.mp4"

win = pygame.display.set_mode((960, 720))
pygame.display.set_caption("parallel playing demo")
clock = pygame.time.Clock()

vid1 = ParallelVideo(PATH1)
vid1.resize((480, 360))
vid1.stop()

vid2 = vid1.copy_sound()
vid2.resize((480, 360))
vid2.stop()

vid3 = ParallelVideo(PATH2)
vid3.resize((480, 360))

vid4 = vid3.copy_sound()
vid4.resize((480, 360))

vid1.play()
vid2.play()

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            vid3.close() 
            vid4.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    clock.tick(60)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (480, 360))
    vid3.draw(win, (480, 0))
    vid4.draw(win, (0, 360))

    pygame.display.update()