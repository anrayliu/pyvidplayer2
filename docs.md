# Video(path, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)

Main object used to play videos. It uses ffmpeg to extract chunks of audio from videos and then feeds it into the pygame music stream. Finally, it uses opencv to display the appropriate video frames.

## Attributes
 - ```path```
 - ```name```
 - ```ext``` - Type of video (mp4, mkv, mov, etc)
 - ```frame_rate``` - How many frames are in one second of the video
 - ```frame_count``` - How many total frames there are
 - ```frame_delay``` - Time in seconds between frames to maintain frame rate
 - ```duration``` - Length of video in seconds
 - ```original_size```
 - ```current_size```
 - ```aspect_ratio``` - Width / height floating point
 - ```chunk_size``` - Amount of audio being extracted at a time, in seconds. Increasing this value will mean less total extracts, but slower extracts.
 - ```max_chunks``` - Maximum amount of extracted audio allowed to be kept in reserve. Increasing this value can help with buffering, but will use more memory.
 - ```max_threads``` - Maximum number of chunks that can be extracted at any given time. Increasing this value can help with buffering, but will increase cpu usage.
 - ```frame_data``` - Current video frame as a numpy array
 - ```frame_surf``` - Current video frame as a pygame surface
 - ```active``` - Video is currently playing. This is unaffected by pausing and resuming.
 - ```buffering``` - Video is waiting for audio to extract.
 - ```paused```
 - ```subs``` - Given Subtitle class
 - ```post_func``` - Given post processing function
 - ```interp``` - Given interpolation algorithm. Linear is fast and effective, cubic is better but increases cpu usage, and area is better for downscaling. 

## Methods
 - ```play()```
 - ```stop()```
 - ```resize(size)```
 - ```change_resolution(height)``` - Given a height, the video will scale its width while maintaining aspect ratio.
 - ```close()```
 - ```restart() ```
 - ```set_volume(volume)``` - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
 - ```get_volume()```
 - ```get_paused()```
 - ```toggle_pause()```
 - ```pause()```
 - ```resume()```
 - ```get_pos()``` - Returns current position in the video in seconds.
 - ```seek(time, relative=True)``` - Changes the current position in the video. If relative is true, the given time will be added or subtracted to the current time. Otherwise, the current position will be set to the given time exactly. Time must be given in seconds, and seeking will be accurate to one tenth of a second.
  - ```draw(surf, pos, force_draw=True)``` - Draws the current video frame onto the given surface, at the given position. If force_draw is true, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This saves cpu usage, but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn. 
 - ```preview()``` - Opens a window and plays the video. This method will hang until the video closes.


# VideoPlayer(path, rect, interactable=True, loop=False, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)

VideoPlayers are GUIs for videos. Think of them like video iframes. Give them a surface and position, and they will play videos under a simple user interface. Currently only supported for pygame.

## Attributes 
 - ```vid``` - Video class of currently playing video
 - ```frame_rect``` - The topleft coordinate, width, and height of the video player
 - ```vid_rect``` - The topleft coordinate, width, and height of the video fitted into the frame_rect
 - ```interactable``` - Enable GUI
 - ```loop``` - Whether video will restart after it finishes. If the queue is not empty, the entire queue will loop, not just the current video.
 - ```queue``` - Videos to play after the current one finishes.

## Methods
 - ```zoom_to_fill()``` - Zooms in the video so that the entire video player is filled in, while maintaining aspect ratio
 - ```zoom_out()```
 - ```queue(path)```
 - ```resize(size)```
 - ```move(pos, relative)``` - Moves the video player. If relative is true, the given coordinates will be added onto the current coordinates. Otherwise, the current coordinates will be set to the given coordinates.
 - ```update(events, show_ui=None)``` - Allows the video player to make its calculations. It must be given the returns of ```pygame.event.get()```. The GUI automatically shows up when your mouse hovers over the video player, so show_ui can be used to override that.
 - ```draw(surf)```
 - ```close()```

# Subtitles(path, colour="white", highlight=(0, 0, 0, 128), font=pygame.font.SysFont("arial", 30), encoding="utf-8-sig")

Object used for handling subtitles. For mostly internal use only. The ```srt``` library has to be installed for subtitles.

## Attributes

 - ```path```
 - ```encoding```
 - ```start``` - Starting timestamp of current subtitle
 - ```end``` - Ending timestamp of current subtitle
 - ```text``` - Current subtitle text
 - ```surf``` - Current text in a pygame Surface
 - ```colour``` - Subtitle font colour
 - ```highlight``` - Subtitle background colour, takes RGBA
 - ```font``` - Pygame font object used to render surfaces

## Methods 

 - ```set_font(font)``` - Takes a pygame font
 - ```get_font()```

# ParallelVideo(path, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR, sound=None)

ParallelVideos play their audio with pygame Sound instead of the music stream. This allows several sounds to be played simultaneously, but control over them such as seeking and pausing is lost. Also, ParallelVideos load their entire audio at once, which can sometimes take a while. This is why for a large amount of ParallelVideos, a VideoCollection is recommended, as it optimizes the loading of audio. 

ParallelVideos have the same attributes and methods as Videos except

 - ```chunks_size```
 - ```max_chunks```
 - ```max_threads```
 - ```buffering```
 - ```paused```
 - ```get_paused()```
 - ```toggle_pause()```
 - ```pause()```
 - ```resume()```
 - ```preview()```
 - ```seek(time, relative=True)```

ParallelVideos have a unique method

 - ```copy_sound(subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)``` - This returns a newly created ParallelVideo, but the sound from the calling object will be given to the new ParallelVideo. This skips the audio loading time.

# VideoCollection()

A VideoCollection is a convenient way to treat multiple ParallelVideos as one. It also optimizes audio loading and playback syncing so this is the recommended way to play videos in parallel.

## Attributes
- ```videos``` - List of ParallelVideos belonging to this collection
- ```positions``` - List of coordinates to draw each video in

## Methods
 - ```add_video(path, rect, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)``` - Creates and adds a new ParallelVideo to the collection. If a video with the same audio has already been loaded, its sound will be copied to optimize load times. The rectangle specifies where the video will be drawn, and what size.
 - ```play()```
 - ```stop()```
 - ```resize(pos)```
 - ```change_resolution(height)```
 - ```set_volume(volume)```
 - ```restart(self)```
 - ```close()```
 - ```draw(surface, force_draw=True)```

# PostProcessing
Used to apply various filters to video playback. Mostly for fun.

 - ```none``` - Default. No post processing 
 - ```blur``` - Slightly blurs frames
 - ```sharpen``` - An okay-looking sharpen. Looks pretty bad for small resolutions
 - ```greyscale``` - Removes colour from frame
 - ```noise``` - Adds a static-like filter. Very intensive.
 - ```letterbox``` - Adds black bars above and below the frame to look more cinematic
 - ```cel_shading``` - Thickens borders for a comic book style filter

# Tkinter and Pyglet Support

To use Tkinter or Pyglet instead of Pygame, use the VideoTkinter and VideoPyglet class respectively, instead of Video. Subtitle support is lost, but they otherwise behave just like a Video. Keep in mind they still use the pygame music stream to play audio. In addition, each ```preview``` method will use their respective graphics API to create a window and draw frames.