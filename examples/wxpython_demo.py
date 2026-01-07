'''
This is a quick example of integrating a video into a wxpython project
Note: wxPython support has been dropped from v0.9.30 and onwards
'''

# Sample videos can be found here: https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import VideoWx
import wx


class Window(wx.Frame):
    def __init__(self):
        super(Window, self).__init__(None, title=f"wx - {vid.name}")

        self.panel = wx.Panel(self, size=wx.Size(*vid.current_size))
        self.panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # for some reason, setting the size of the frame in constructor
        # still clips off some of the video
        # this seems to work for now

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.panel)
        sizer.Fit(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel)
        sizer.Fit(self)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.panel.Bind(wx.EVT_PAINT, self.draw)

        vid.play()
        self.timer.Start(int(1000 / vid.frame_rate))

        self.Show()

    def update(self, event):
        if not vid.active:
            wx.CallAfter(self.Close)

        self.panel.Refresh(eraseBackground=False)

    def draw(self, event):
        vid.draw(self.panel, (0, 0), False)


class MyApp(wx.App):
    def OnInit(self):
        Window()
        return True


vid = VideoWx("resources//clip.mp4")

app = MyApp(False)
app.MainLoop()
vid.close()
