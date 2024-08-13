from setuptools import setup
# from pyvidplayer2._version import __version__
# version = {"version": __version__}
# or:
version = {}
with open("pyvidplayer2/_version.py") as f:
    exec(f.read(), version)


with open("README.md", 'r') as f:
    long_desc = f.read()


setup(
    name="pyvidplayer2",
    version=version["__version__"],
    description="Reliable, easy, and fast video playback in Python",
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
    url="https://github.com/anrayliu/pyvidplayer2",
    platforms=["windows", "linux"],
    keywords=["pygame", "video", "playback", "tkinter", "pyqt", "pyglet", "youtube", "stream"]
)