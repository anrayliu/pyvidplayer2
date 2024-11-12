'''
This demo shows how subtitle files from Youtube can be fetched and used
If a subtitle file in the preferred language is not available, automatic captions are used
'''



from pyvidplayer2 import Video, Subtitles
import pygame


# if you don't know Google's language code for a particular area, which can be pretty
# difficult to find sometimes, I've found success asking chatGPT for them


Video("https://www.youtube.com/watch?v=qyCVCGg_3Ec", youtube=True, max_res=720,
      subs=Subtitles("https://www.youtube.com/watch?v=qyCVCGg_3Ec", youtube=True, pref_lang="en")).preview()
