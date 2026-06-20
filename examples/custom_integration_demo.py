'''
This demo shows how to use VideoCustom to integrate with any
graphics library, using pyplot as an example

pip install matplotlib
'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pyvidplayer2.video_custom import VideoCustom


# processed video frames are BGR format
def bgr2rgb(data):
    return data[:, :, ::-1]


v = VideoCustom("resources/billiejean.mp4", post_process=bgr2rgb)
v.seek_frame(0)  # load in first frame

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

frame = ax.imshow(v.frame_data)


def update_func(_):
    if not v.active:
        plt.close(fig)
        return [frame]

    # to integrate with an unsupported graphics library,
    # call update() manually

    # if a frame is ready to be rendered, the method
    # will return True
    # access the frame as a NumPy image with .frame_data

    if v.update():
        frame.set_data(v.frame_data)

    return [frame]


ani = animation.FuncAnimation(fig, update_func, interval=5, blit=True, save_count=0)
plt.show()

v.close()
