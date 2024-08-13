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
    # license="MIT",
    packages=["pyvidplayer2"],
    install_requires=["numpy",
                    "opencv_python",
                    "pygame",
                    "pysubs2",
                    "PyAudio"],
    url="https://github.com/anrayliu/pyvidplayer2",
    platforms=["windows", "linux"],
    keywords=["pygame", "video", "playback", "tkinter", "pyqt", "pyglet", "youtube", "stream"],
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Software Development :: Libraries :: pygame",

        # Pick your license as you wish (see also "license" above)
        "License :: OSI Approved :: MIT License",

        # Specify the Python versions you support here.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]
)