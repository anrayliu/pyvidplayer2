from setuptools import setup
from pyvidplayer2._version import __version__


with open("README.md", 'r') as f:
    long_desc = f.read()


setup(
    name="pyvidplayer2",
    version=__version__,
    description="Reliable, easy, and fast video playback in Python",
    long_description=long_desc,
    long_description_content_type = "text/markdown",
    author="Anray Liu",
    author_email="anrayliu@gmail.com",
    packages=["pyvidplayer2"],
    install_requires=["numpy",
                    "opencv_python",
                    "pygame",
                    "pysubs2",
                    "PyAudio"],
    url="https://github.com/anrayliu/pyvidplayer2",
    platforms=["windows", "linux", "macos"],
    keywords=["pygame", "video", "playback", "tkinter", "pyqt", "pyside", "pyglet", "raylib", "youtube", "stream"],
    python_requires=">=3.9",
    classifiers = [
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Software Development :: Libraries :: pygame",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ]
)