'''
This is an example showing how to add subtitles to a video
'''


from pyvidplayer2 import Subtitles, Video
from pygame import Font


# regular subtitles playback

with Video(r"resources\trailer2.mp4", subs=Subtitles(r"resources\subs2.srt")) as v:
    v.preview()

# multiple subtitle tracks

with Video(r"resources\trailer1.mp4", subs=[Subtitles(r"resources\subs1.srt"), Subtitles(r"resources\subs2.srt")]) as v:
    v.preview()

# custom subtitles

subs = Subtitles(r"resources\subs2.srt", font=Font(r"resources\font.ttf", 60), highlight=(255, 0, 0, 128), offset=500)
with Video(r"resources\trailer2.mp4", subs=subs) as v:
    v.preview()

# set a delay for subtitles

with Video(r"resources\trailer2.mp4", subs=Subtitles(r"resources\subs2.srt", delay=-3)) as v:
    v.preview()

# you can also use subtitles from within a video by specifying which track it belongs to
# e.g Subtitles("video_file_with_subs", track_index=0)  # uses the subtitles from the first track
