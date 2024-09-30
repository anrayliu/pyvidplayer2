[![下载的](https://static.pepy.tech/badge/pyvidplayer2)](http://pepy.tech/project/pyvidplayer2)

# pyvidplayer2（请报告所有的错误）
语言: [English](https://github.com/anrayliu/pyvidplayer2/blob/main/README.md) | 中文

pyvidplayer2 是 pyvidplayer 的继任者，它在几乎所有方面都要更好，现在我们终于可以轻松可靠地用 Python 播放视频。

所有原始库中的功能都已移植过来，唯一的例外是 `alt_resize()`。由于 pyvidplayer2 有一个完全重建的基础，`set_size()` 的不可靠性已被消除，因此现在不再需要备用函数。

# 特性（请参阅示例文件夹）
- 易于实现（4行代码）
- 快速可靠
- 调整播放速度
- 反向视频播放
- 没有音视频同步问题
- 字幕支持（.srt，.ass等）
- 同时播放多个视频
- 内置图形用户界面（GUI）
- 支持 Pygame、PygameCE, Pyglet、Tkinter 和 PyQT6
- 可以播放所有 FFMPEG 支持的视频格式
- 后期处理效果
- 摄像头视频捕获
- 播放 Youtube 的视频
- 播放 RAM 中的视频
- 播放可变帧率的视频 (VFR)

# 安装
```
pip install pyvidplayer2
```

注意：必须安装并通过系统 PATH 访问 FFMPEG（仅需要基本组件）。这里有一篇关于如何在 Windows 上执行此操作的在线文章：
https://phoenixnap.com/kb/ffmpeg-windows。
某些功能可能还需要 FFPROBE - 这应该与 FFMPEG 下载捆绑在一起。

## Linux

在运行 `pip install pyvidplayer2` 之前，您必须先安装所需的开发包。

例如，在 Ubuntu/Debian 上执行以下命令安装所需的依赖项：

```
sudo apt-get install build-essential python3-dev portaudio19-dev
```
Python 和 PortAudio 的开发包分别解决了缺少 Python.h 和 portaudio.h 的问题

# 快速入门

查看示例文件夹以获取更多基本指南，documentation.md 中有包含更详细的信息。

```
import pygame
from pyvidplayer2 import Video


# 创建视频对象

vid = Video("video.mp4")

win = pygame.display.set_mode(vid.current_size)
pygame.display.set_caption(vid.name)


while vid.active:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.stop()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    if key == "r":
        vid.restart()           # 重播视频到开头
    elif key == "p":
        vid.toggle_pause()      # 暂停/播放视频
    elif key == "m":
        vid.toggle_mute()       # 静音/取消静音视频
    elif key == "right":
        vid.seek(15)            # 跳过视频中的15秒
    elif key == "left":
        vid.seek(-15)           # 倒回视频中的15秒
    elif key == "up":
        vid.set_volume(1.0)     # 最大音量
    elif key == "down":
        vid.set_volume(0.0)     # 最小音量

    # 只绘制新帧，并且只在绘制了内容时更新屏幕
    
    if vid.draw(win, (0, 0), force_draw=False):
        pygame.display.update()

    pygame.time.wait(16) # 大约60帧每秒


# 完成后关闭视频

vid.close()
pygame.quit()
```

# 依赖项
```
numpy
opencv_python
```

## 可选包
```
pygame（图形和音频库，已安装）
PyAudio（音频库，已安装）
pysubs2（用于字幕，已安装）
yt_dlp（用于流式传输 YouTube 视频）
imageio（用于字节格式的视频）
pyglet（图形库）
PyQt6（图形库）
```

# 已知问题（截至 v0.9.23）

 - Youtube 视频有时会冻结或卡顿（罕见）
 - 从字节读取时，视频搜索速度较慢
 - 从字节播放时旋转的视频将按其原始方向显示
