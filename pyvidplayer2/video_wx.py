from typing import Callable, Union, Tuple
import wx
import numpy as np
from .video import Video, READER_AUTO
from .post_processing import PostProcessing


class VideoWx(Video):
    """
    Refer to "https://github.com/anrayliu/pyvidplayer2/blob/main/documentation.md" for detailed documentation.
    """

    def __init__(self, path: Union[str, bytes], chunk_size: float = 10, max_threads: int = 1, max_chunks: int = 1,
                 post_process: Callable[[np.ndarray], np.ndarray] = PostProcessing.none,
                 interp: Union[str, int] = "linear", use_pygame_audio: bool = False, reverse: bool = False,
                 no_audio: bool = False, speed: float = 1, youtube: bool = False,
                 max_res: int = 720, as_bytes: bool = False, audio_track: int = 0, vfr: bool = False,
                 pref_lang: str = "en", audio_index: int = None, reader: int = READER_AUTO, cuda_device: int = -1) -> None:
        Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio,
                       reverse, no_audio, speed, youtube, max_res,
                       as_bytes, audio_track, vfr, pref_lang, audio_index, reader, cuda_device)

    def _create_frame(self, data: np.ndarray):
        h, w = data.shape[:2]
        if self.colour_format == "BGR":
            data = data[..., ::-1]  # converts to RGB
        return wx.Image(w, h, data.flatten().tobytes()).ConvertToBitmap()

    def _render_frame(self, panel: wx.Panel, pos: Tuple[int, int]):
        dc = wx.PaintDC(panel)
        dc.DrawBitmap(self.frame_surf, pos[0], pos[1], True)

    def draw(self, panel: wx.Panel, pos: Tuple[int, int], force_draw: bool = True) -> bool:
        if (self._update() or force_draw) and self.frame_surf is not None:
            self._render_frame(panel, pos)
            return True
        return False

    def preview(self_video, max_fps: int = 60) -> None:
        class Window(wx.Frame):
            def __init__(self_frame):
                super(Window, self_frame).__init__(None, title=f"wx - {self_video.name}")

                self_frame.panel = wx.Panel(self_frame, size=wx.Size(*self_video.current_size))
                self_frame.panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)

                # for some reason, setting the size of the frame in constructor
                # still clips off some of the video
                # this seems to work for now

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(self_frame.panel)
                sizer.Fit(self_frame)
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(self_frame.panel)
                sizer.Fit(self_frame)

                self_frame.timer = wx.Timer(self_frame)
                self_frame.Bind(wx.EVT_TIMER, self_frame.update, self_frame.timer)
                self_frame.panel.Bind(wx.EVT_PAINT, self_frame.draw)

                self_video.play()
                self_frame.timer.Start(int(1000 / self_video.frame_rate))

                self_frame.Show()

            def update(self_frame, event):
                if not self_video.active:
                    wx.CallAfter(self_frame.Close)

                self_frame.panel.Refresh(eraseBackground=False)

            def draw(self_frame, event):
                self_video.draw(self_frame.panel, (0, 0), False)

        class MyApp(wx.App):
            def OnInit(self):
                Window()
                return True

        app = MyApp(False)
        app.MainLoop()
        self_video.close()
