import pygame
from pyvidplayer2 import ParallelVideo


win = pygame.display.set_mode((960, 360))
pygame.display.set_caption("parallel playing demo")
clock = pygame.time.Clock()

vid1 = ParallelVideo(r"resources\trailer.mp4")
vid1.resize((480, 360))

vid2 = vid1.copy_sound()
vid2.resize((480, 360))

# sync the audio from both videos

vid1.play() 
vid2.play()


while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid1.close()
            vid2.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    clock.tick(60)
        
    vid1.draw(win, (0, 0))
    vid2.draw(win, (480, 0))

    pygame.display.update()