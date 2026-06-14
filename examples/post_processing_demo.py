'''
This example gives a side by side comparison between a few available post process effects
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


import pygame
from pyvidplayer2 import PostProcessing, Video

PATH = r"resources\birds.avi"

win = pygame.display.set_mode((576, 720))
pygame.display.set_caption("post processing demo")

# supply a post processing function here
# you can use provided ones from the PostProcessing class, or you can make your own
# all post processing functions must accept and return a numpy ndarray
# post processing functions are applied to each frame before rendering
# both the frame_data and frame_surf properties have post processing applied to them


def custom_post_processing(data):
    return data     # do nothing with the frame


def custom_chain(data):
    return PostProcessing.vhs(
        PostProcessing.fliplr(
            PostProcessing.blur(
                PostProcessing.noise(
                    data
                )
            )
        )
    )


videos = [Video(PATH, post_process=PostProcessing.emboss),
          Video(PATH, post_process=custom_chain),
          Video(PATH, post_process=PostProcessing.greyscale)]
for vid in videos:
    vid.change_resolution(240)

font = pygame.font.SysFont("arial", 30)
surfs = [font.render("Emboss", True, "white"),
         font.render("Normal", True, "white"),
         font.render("Greyscale", True, "white")]


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            [video.close() for video in videos]
            pygame.quit()
            exit()

    pygame.time.wait(16)

    for i, surf in enumerate(surfs):
        y = 240 * i
        videos[i].draw(win, (0, y))
        pygame.draw.rect(win, "black", (0, y, *surf.get_size()))
        win.blit(surf, (0, y))

    pygame.display.update()
