'''
This demo shows how multiple subtitles can be played at once 
'''


from pyvidplayer2 import Video, Subtitles 


# pass a list of subtitles objects 

Video("resources\\trailer1.mp4", subs=[Subtitles("resources\\subs1.srt"),
                                       Subtitles("resources\\subs2.srt", offset=150)]).preview() 
