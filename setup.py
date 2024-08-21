from setuptools import setup
from pyvidplayer2 import VERSION


with open("README.md", 'r') as f:
    long_desc = f.read()


setup(
    name="pyvidplayer2",
    version=VERSION,
    description="Video playback in Python",
    long_description=long_desc,
    long_description_content_type = "text/markdown",
    author="Anray Liu",
    author_email="anrayliu@gmail.com",
    license="MIT",
    packages=["pyvidplayer2"],
    install_requires=["numpy",
                    "opencv_python",
                    "pygame",
                    "pysubs2",
                    "PyAudio"],
    url="https://github.com/ree1261/pyvidplayer2",
    platforms=["windows", "linux"],
    keywords=["pygame", "video", "playback", "tkinter", "pyqt", "pyglet", "youtube", "stream"],
    python_requires=">=3.9"
)