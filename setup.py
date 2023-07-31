from setuptools import setup


with open("README.md", 'r') as f:
    long_desc = f.read()


setup(
    name="pyvidplayer2",
    version="0.9.3",
    description="Video playback in Python",
    long_description=long_desc,
    long_description_content_type = "text/markdown",
    author="Anray Liu",
    author_email="anrayliu@gmail.com",
    license="MIT",
    packages=["pyvidplayer2"],
    install_requires=["numpy==1.24.3",
                    "opencv_python==4.7.0.72",
                    "pygame==2.4.0",
                    "srt==3.5.3",
                    "PyAudio==0.2.13"],
    url="https://github.com/ree1261/pyvidplayer2",
    platforms=["windows"],
    keywords=["pygame", "video", "playback"],
)