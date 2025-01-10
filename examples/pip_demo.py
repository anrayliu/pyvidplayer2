'''
A quick example showing how pyvidplayer2 can be used in more complicated applications
This is a Picture-in-Picture app

install pywin32 via pip before using
'''


import pygame
from win32gui import SetWindowPos, GetCursorPos, GetWindowRect, GetForegroundWindow, SetForegroundWindow
from win32api import GetSystemMetrics
from win32con import SWP_NOSIZE, HWND_TOPMOST
from win32com.client import Dispatch
from pyvidplayer2 import VideoPlayer, Video


SIZE = (426, 240)
FILE = r"resources\billiejean.mp4"

win = pygame.display.set_mode(SIZE, pygame.NOFRAME)
pygame.display.set_caption("pip demo")

# creates the video player

vid = VideoPlayer(Video(FILE, interp="area"), (0, 0, *SIZE), interactable=True)

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

    try:
        touching = pygame.Rect(GetWindowRect(hwnd)).collidepoint(GetCursorPos())
    except: # windows is buggy
        touching = False 

    if touching and GetForegroundWindow() != hwnd:

        # weird behaviour with SetForegroundWindow that requires the alt key to be pressed before it's called

        shell.SendKeys("%")
        try:
            SetForegroundWindow(hwnd)
        except: # catches weird errors
            pass    

    # handles video playback

    vid.update(events, show_ui=touching)
    vid.draw(win)

    pygame.display.update()
