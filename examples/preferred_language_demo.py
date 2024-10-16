''' 
This example shows how you can specify different language tracks when streaming from Youtube

Simply provide the language codes in pref_lang
For a full list of codes, refer to https://developers.google.com/admin-sdk/directory/v1/languages
'''

from pyvidplayer2 import Video 

# en is Google's code for English

Video("https://www.youtube.com/watch?v=D-hLh63iuSI", youtube=True, pref_lang="en").preview()
