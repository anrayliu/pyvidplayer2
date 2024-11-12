from pyvidplayer2 import * 
import os


videos = ["billiejean.mp4", "birds.avi", "clip.mp4", "gray.avi", "gray.mp4", "medic.mov", "trailer1.mp4", "trailer2.mp4"]
subtitles = ["subs1.srt", "subs2.srt"]


def test_open_video():
   for v in videos:
      assert isinstance(Video(os.path.join("resources", v)), Video)

def test_local_subtitles():
   for v in videos:
      for s in subtitles:
         vid = Video(os.path.join("resources", v), subs=Subtitles(os.path.join("resources", s)))
         assert vid.subs[0].path == os.path.join("resources", s)
