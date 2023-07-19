from setuptools import setup

setup(
    name="pyvidplayer2",
    version="1.0",
    description="Video playback in Python",
    author="Anray Liu",
    author_email="anrayliu@gmail.com",
    packages=["pyvidplayer2"],
    install_requires=["numpy==1.24.3",
                    "opencv_python==4.7.0.72",
                    "pygame==2.4.0"],
    url="https://github.com/ree1261/pyvidplayer2"
)