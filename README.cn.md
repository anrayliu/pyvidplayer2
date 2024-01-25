# pyvidplayer2（请报告所有的错误！）
语言: [English](https://github.com/anrayliu/pyvidplayer2/blob/Update-README/README.md) | 中文

介绍 pyvidplayer2，它是 pyvidplayer 的继任者。在几乎所有方面都更好，终于可以轻松可靠地在 Python 中播放视频。

所有原始库中的功能都已移植过来，唯一的例外是 `alt_resize()`。由于 pyvidplayer2 有一个完全重建的基础，`set_size()` 的不可靠性已被消除，因此现在不再需要备用函数。

# 特性（在 Windows 上测试）
- 易于实现（4行代码）
- 快速可靠
- 调整播放速度
- 没有音视频同步问题
- 字幕支持（.srt，.ass等）
- 并行播放多个视频
- 内置图形用户界面（GUI）
- 支持 Pygame、Pyglet、Tkinter 和 PyQT6
- 可以播放所有 ffmpeg 支持的视频格式
- 后期处理效果
- 摄像头视频捕获

# 安装
pip install pyvidplayer2

注意：必须安装并通过系统 PATH 访问 FFMPEG（仅需要基本组件）。这里有一篇关于如何在 Windows 上执行此操作的在线文章：
https://phoenixnap.com/kb/ffmpeg-windows。

# 快速入门

查看示例文件夹以获取更多基本指南，documentation.md 包含更详细的信息。

```python
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
    elif key == "1":
        vid.set_speed(1.0)      # 正常播放速度
    elif key == "2":
        vid.set_speed(2.0)      # 倍速播放视频

    # 只绘制新帧，并且只在绘制了内容时更新屏幕
    
    if vid.draw(win, (0, 0), force_draw=False):
        pygame.display.update()

    pygame.time.wait(16) # 大约60帧每秒


# 完成后关闭视频

vid.close()
pygame.quit()

