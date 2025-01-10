'''
This demo shows how subtitle files from Youtube can be fetched and used
If a subtitle file in the preferred language is not available, automatic captions are used
'''



from pyvidplayer2 import Video, Subtitles
import pygame


# if you don't know Google's language code for a particular area, which can be pretty
# difficult to find sometimes, I've found success asking chatGPT for them

# if no subtitles are provided for the video, automatically generated captions are used
# generated captions are automatically translated, so you can request captions from any language

# that being said, the default subtitles font cannot display many characters like Korean or Japanese

with Video("https://www.youtube.com/watch?v=qyCVCGg_3Ec", youtube=True, max_res=720,
      subs=Subtitles("https://www.youtube.com/watch?v=qyCVCGg_3Ec", youtube=True, pref_lang="en")) as v:
      v.preview()
