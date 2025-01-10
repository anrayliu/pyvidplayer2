'''
This is a quick example of integrating a video into a tkinter project
'''


import tkinter
from pyvidplayer2 import VideoTkinter

video = VideoTkinter(r"resources\trailer1.mp4")

def update():
    video.draw(canvas, (video.current_size[0] / 2, video.current_size[1] / 2), force_draw=False)
    if video.active:
        root.after(16, update) # for around 60 fps
    else:
        root.destroy()

root = tkinter.Tk()
root.title(f"tkinter support demo")

canvas = tkinter.Canvas(root, width=video.current_size[0], height=video.current_size[1], highlightthickness=0)
canvas.pack()

update()
root.mainloop()

video.close()
