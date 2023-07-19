import pygame
from win32gui import SetWindowPos, GetCursorPos, GetWindowRect, GetForegroundWindow, SetForegroundWindow
from win32api import GetSystemMetrics
from win32con import SWP_NOSIZE, HWND_TOPMOST
from win32com.client import Dispatch
from pyvidplayer2 import VideoPlayer, PostProcessing


# try playing with these values

SIZE = (426, 240)
FILE = "demos\\vids\\sh.mp4"

win = pygame.display.set_mode(SIZE, pygame.NOFRAME)

# creates the video player

vid = VideoPlayer(FILE, (0, 0, *SIZE), interp=PostProcessing.INTER_AREA, post_process=PostProcessing.cel_shading)

# moves the window to the bottom right corner and pins it above other windows

hwnd = pygame.display.get_wm_info()["window"]

SetWindowPos(hwnd, HWND_TOPMOST, GetSystemMetrics(0) - SIZE[0], GetSystemMetrics(1) - SIZE[1] - 48, 0, 0, SWP_NOSIZE)

clock = pygame.time.Clock()

shell = Dispatch("WScript.Shell")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            quit() 

    clock.tick(60)

    # allows the ui to be seamlessly interacted with

    touching = pygame.Rect(GetWindowRect(hwnd)).collidepoint(GetCursorPos())
    if touching and GetForegroundWindow() != hwnd:

        # weird behaviour with SetForegroundWindow that requires the alt key to be pressed before it
        
        shell.SendKeys("%")

        SetForegroundWindow(hwnd)

    # handles video playback

    vid.update(events, show_ui=touching)
    vid.draw(win)

    pygame.display.update()