Full unit tests for pyvidplayer2 v0.9.29

Requires the resources folder which contains all the test videos
Download the videos here: https://github.com/anrayliu/pyvidplayer2-test-resources
Requires all optional dependencies: `pip install pyvidplayer2[all]`

If the installation isn't working, you can remove problematic packages from 
`requirements.txt` and install locally with `pip install .`

Also requires the package `sounddevice`

Note: Some tests can be inconsistent, depending on your computer specs
My 5600x has no issues, while my 7530U sometimes struggles

Problematic tests should have a comment marking them

Feel free to open an issue if needed.