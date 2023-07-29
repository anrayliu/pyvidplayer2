# Video(path, chunk_size=300, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)

Main object used to play videos. It uses FFMPEG to extract chunks of audio from videos and then feeds it into the Pygame music stream. Finally, it uses OpenCV to display the appropriate video frames.

## Arguments
```path``` - Path to video file. I tested a few popular video types, such as mkv, mp4, mov, avi, and 3gp, but theoretically anything FFMPEG can extract data from should work.
```chunk_size``` - How much audio is extracted at a time, in seconds. Increasing this value can mean less total extracts, but slower extracts.
```max_threads``` - Maximum number of chunks that can be extracted at any given time. Increasing this value can speed up extract at the expense of cpu usage.
```max_chunks``` - Maximum number of chunks allowed to be extracted and reserved. Increasing this value can help with buffering, but will use more memory.
```subs``` - Pass a Subtitle class here for the video to display subtitles.
```post_process``` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place.
```interp``` - Interpolation technique used when resizing frames. In general, the three main ones are cv2.INTER_LINEAR, which is balanced, cv2.INTER_CUBIC, which is slower but produces better results, and cv2.INTER_AREA, which is better for downscaling.

## Attributes
 - ```path``` - Same as given argument.
 - ```name``` - Name of file without the directory and extension.
 - ```ext``` - Type of video (mp4, mkv, mov, etc).
 - ```frame_rate``` - How many frames are in one second.
 - ```frame_count``` - How many total frames there are.
 - ```frame_delay``` - Time between frames in order to maintain frame rate (in fractions of a second).
 - ```duration``` - Length of video in seconds.
 - ```original_size```
 - ```current_size```
 - ```aspect_ratio``` - Width divided by height.
 - ```chunk_size``` - Same as given argument.
 - ```max_chunks``` - Same as given argument.
 - ```max_threads``` - Same as given argument.
 - ```frame_data``` - Current video frame as a NumPy ndarray.
 - ```frame_surf``` - Current video frame as a Pygame Surface.
 - ```active``` - Whether the video is currently playing. This is unaffected by pausing and resuming.
 - ```buffering``` - Whether the video is waiting for audio to extract.
 - ```paused```
 - ```subs``` - Same as given argument.
 - ```post_func``` - Same as given argument.
 - ```interp``` - Same as given argument.

## Methods
 - ```play()```
 - ```stop()```
 - ```resize(size)```
 - ```change_resolution(height)``` - Given a height, the video will scale its width while maintaining aspect ratio.
 - ```close()``` - Releases resources. Always recommended to call when done.
 - ```restart() ```
 - ```set_volume(volume)``` - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
 - ```get_volume()```
 - ```get_paused()```
 - ```toggle_pause()``` - Pauses if the video is playing, and resumes if the video is paused.
 - ```pause()```
 - ```resume()```
 - ```get_pos()``` - Returns the current position in seconds.
 - ```seek(time, relative=True)``` - Changes the current position in the video. If relative is true, the given time will be added or subtracted to the current time. Otherwise, the current position will be set to the given time exactly. Time must be given in seconds, and seeking will be accurate to one tenth of a second.
  - ```draw(surf, pos, force_draw=True)``` - Draws the current video frame onto the given surface, at the given position. If force_draw is true, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces cpu usage, but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn. 
 - ```preview()``` - Opens a window and plays the video. This method will hang until the video closes. Videos are played at 60 fps with force_draw disabled.

# VideoPlayer(video, rect, interactable=True, loop=False, preview_thumbnails=0)

VideoPlayers are GUI containers for videos. This seeks to mimic standard video players, so clicking it will play/pause playback, and the GUI will only show when the mouse is hovering over it.

## Arguments
```video``` - Video object to play.
```rect``` - An x, y, width, and height of the VideoPlayer. The topleft corner will be the x, y coordinate.
```interactable``` - Enables the GUI.
```loop``` - Whether the contained video will restart after it finishes. If the queue is not empty, the entire queue will loop, not just the current video.
```preview_thumbnails``` - Number of preview thumbnails loaded and saved in memory. When seeking, a preview window will show the closest loaded frame. The higher this number is, the more frames are loaded, increasing the preview accuracy, but also increasing initial load time and memory usage. Because of this, this value is defaulted to 0, which turns seek previewing off.

## Attributes 
 - ```video``` - Same as given argument.
 - ```frame_rect``` - Same as given argument.
 - ```vid_rect``` - This is the video fitted into the frame_rect while maintaining aspect ratio. Black bars will appear in any unused space.
 - ```interactable``` - Same as given argument.
 - ```loop``` - Same as given argument.
 - ```queue``` - Videos to play after the current one finishes.
 - ```preview_thumbnails``` - Same as given argument.

## Methods
 - ```zoom_to_fill()``` - Zooms in the video so that the entire frame_rect is filled in, while maintaining aspect ratio.
 - ```zoom_out()``` - Reverts zoom_to_fill()
 - ```queue(path)```
 - ```resize(size)```
 - ```move(pos, relative)``` - Moves the VideoPlayer. If relative is true, the given coordinates will be added onto the current coordinates. Otherwise, the current coordinates will be set to the given coordinates.
 - ```update(events, show_ui=None)``` - Allows the VideoPlayer to make calculations. It must be given the returns of pygame.event.get(). The GUI automatically shows up when your mouse hovers over the video player, so show_ui can be used to override that. This method also returns show_ui.
 - ```draw(surface)``` - Draws the VideoPlayer onto the given Surface.
 - ```close()``` - Releases resources. Always recommended to call when done.

# Subtitles(path, colour="white", highlight=(0, 0, 0, 128), font=pygame.font.SysFont("arial", 30), encoding="utf-8-sig")

Object used for handling subtitles.

## Arguments
```path``` - Path to subtitle file. Currently only srt files are supported.
```colour``` - Colour of text.
```highlight``` - Background colour of text. Accepts RGBA, so it can be made completely transparent.
```font``` - Pygame Font or SysFont object used to render Surfaces. This includes the size of the text.
```encoding``` - Encoding used to open the srt file.

## Attributes

 - ```path``` - Same as given argument.
 - ```encoding``` - Same as given argument.
 - ```start``` - Starting timestamp of current subtitle.
 - ```end``` - Ending timestamp of current subtitle.
 - ```text``` - Current subtitle text.
 - ```surf``` - Current text in a Pygame Surface.
 - ```colour``` - Same as given argument.
 - ```highlight``` - Same as given argument.
 - ```font``` - Same as given argument.

## Methods 

 - ```set_font(font)```
 - ```get_font()```

# ParallelVideo(path, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)

ParallelVideos play their audio with the Pygame Sound object instead of the music stream. This allows several sounds to be played simultaneously, but control over them such as seeking and pausing is lost. Also, ParallelVideos load their entire audio at once, which can sometimes take a while. This is why for a large amount of ParallelVideos, a VideoCollection is recommended, as it optimizes the loading of audio.

## Arguments
```path``` - Path to video file. I tested a few popular video types, such as mkv, mp4, mov, avi, and 3gp, but theoretically anything FFMPEG can extract data from should work.
```subs``` - Pass a Subtitle class here for the video to display subtitles.
```post_process``` - Post processing function that is applied whenever a frame is rendered. This is PostProcessing.none by default, which means no alterations are taking place.
```interp``` - Interpolation technique used when resizing frames. In general, the three main ones are cv2.INTER_LINEAR, which is balanced, cv2.INTER_CUBIC, which is slower but produces better results, and cv2.INTER_AREA, which is better for downscaling.

## Attributes
 - ```path``` - Same as given argument.
 - ```name``` - Name of file without the directory and extension.
 - ```ext``` - Type of video (mp4, mkv, mov, etc).
 - ```frame_rate``` - How many frames are in one second.
 - ```frame_count``` - How many total frames there are.
 - ```frame_delay``` - Time between frames in order to maintain frame rate (in fractions of a second).
 - ```duration``` - Length of video in seconds.
 - ```original_size```
 - ```current_size```
 - ```aspect_ratio``` - Width divided by height.
 - ```frame_data``` - Current video frame as a NumPy ndarray.
 - ```frame_surf``` - Current video frame as a Pygame Surface.
 - ```active``` - Whether the video is currently playing. This is unaffected by pausing and resuming.
 - ```subs``` - Same as given argument.
 - ```post_func``` - Same as given argument.
 - ```interp``` - Same as given argument.

 ## Methods
 - ```play()```
 - ```stop()```
 - ```resize(size)```
 - ```change_resolution(height)``` - Given a height, the video will scale its width while maintaining aspect ratio.
 - ```close()``` - Releases resources. Always recommended to call when done.
 - ```restart() ```
 - ```set_volume(volume)``` - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
 - ```get_volume()```
 - ```get_pos()``` - Returns the current position in seconds.
 - ```draw(surf, pos, force_draw=True)``` - Draws the current video frame onto the given surface, at the given position. If force_draw is true, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces cpu usage, but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn. 
 - ```copy_sound(subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)``` - This returns a newly created ParallelVideo, but the sound from the calling object will be given to the new ParallelVideo. This skips the audio loading time.

# VideoCollection()

A VideoCollection is a convenient way to treat multiple ParallelVideos as one. It also optimizes audio loading and playback syncing so this is the recommended way to play videos in parallel. When a method such as play() is called, it will be called for every video in the collection.

## Attributes
- ```videos``` - List of ParallelVideos belonging to this collection.
- ```positions``` - List of coordinates to draw each video at.

## Methods
 - ```add_video(path, rect, subs=None, post_process=PostProcessing.none, interp=cv2.INTER_LINEAR)``` - Creates and adds a new ParallelVideo to the collection. If a video with the same audio has already been loaded, its sound will be copied to optimize load times. The rectangle specifies where the video will be drawn, and what size.
 - ```play()```
 - ```stop()```
 - ```resize(pos)```
 - ```change_resolution(height)``` - Given a height, the video will scale its width while maintaining aspect ratio.
 - ```set_volume(volume)``` - Adjusts the volume of the video, from 0.0 (min) to 1.0 (max).
 - ```restart(self)```
 - ```close()``` - Releases resources. Always recommended to call when done.
 - ```draw(surface, force_draw=True)``` - Draws the current video frame onto the given surface, at the given position. If force_draw is true, a surface will be drawn every time this is called. Otherwise, only new frames will be drawn. This reduces cpu usage, but will cause flickering if anything is drawn under or above the video. This method also returns whether a frame was drawn. 

# PostProcessing
Used to apply various filters to video playback. Mostly for fun.

 - ```none``` - Default. Nothing happens.
 - ```blur``` - Slightly blurs frames.
 - ```sharpen``` - An okay-looking sharpen. Looks pretty bad for small resolutions.
 - ```greyscale``` - Removes colour from frame.
 - ```noise``` - Adds a static-like filter. Very intensive.
 - ```letterbox``` - Adds black bars above and below the frame to look more cinematic.
 - ```cel_shading``` - Thickens borders for a comic book style filter.

# Other Supported Graphics Libraries

 - Tkinter (```VideoTkinter```)
 - Pyglet (```VideoPyglet```)
 - PyQT6 (```VideoPyQT```)

To use other libraries instead of Pygame, use their respective video object. Subtitle support is lost, but they otherwise behave just like a Video. Keep in mind they still use the Pygame music stream to play audio. In addition, each preview method will use their respective graphics API to create a window and draw frames.
