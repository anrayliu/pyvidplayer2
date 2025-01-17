'''
This is an example showing off a draggable webcam app

install pywin32 via pip before using
'''

import pygame
from pyvidplayer2 import Webcam
import win32api, win32gui, win32con
from win32com.client import Dispatch


webcam = Webcam(interp="area", capture_size=(1920, 1080))
webcam.change_resolution(240)   # scales video without changing aspect ratio

print(f"Webcam capturing at {webcam.original_size[1]}p resolution, scaling to {webcam.current_size[1]}p for display")

win = pygame.display.set_mode(webcam.current_size, pygame.NOFRAME)
pygame.display.set_caption("webcam app demo")
clock = pygame.time.Clock()

dragging = False 
temp_pos = (0, 0)
window_rect = pygame.Rect(win32api.GetSystemMetrics(0) - win.get_width(), win32api.GetSystemMetrics(1) - win.get_height() - 48, *win.get_size())
shell = Dispatch("WScript.Shell") # required workaround for a windows bug

HWND = pygame.display.get_wm_info()["window"]

# makes window topmost
win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, *window_rect, win32con.SWP_NOSIZE)

while True:
    mouse_movement = (0, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            webcam.close()
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True 
            temp_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEMOTION:
            mouse_movement = event.pos

    if dragging:
        if not pygame.mouse.get_pressed()[0]:
            dragging = False 
        elif mouse_movement != (0, 0):
                window_rect.x += mouse_movement[0] - temp_pos[0]
                window_rect.y += mouse_movement[1] - temp_pos[1]
            
                # moves window while keeping topmost
                win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, *window_rect, win32con.SWP_NOSIZE)

    # keeps the webcam focused when hovered over for seamless dragging
    try:
        touching = window_rect.collidepoint(win32api.GetCursorPos())
    except: # catches access denied when pc goes to sleep
        touching = False

    if win32gui.GetForegroundWindow() != HWND and touching:
        shell.SendKeys("%") # windows is weird

        # windows is buggy
        try:
            win32gui.SetForegroundWindow(HWND)
        except:
            pass
    
    clock.tick(60)
    
    webcam.draw(win, (0, 0), force_draw=False)
    
    pygame.display.update()
