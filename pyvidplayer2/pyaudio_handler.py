import pyaudio
import wave
import math 
import time
import numpy
from threading import Thread
from io import BytesIO


_p = pyaudio.PyAudio()


class PyaudioHandler:
    def __init__(self) -> None:
        self.stream = None
        self.wave = None

        self.thread = None
        self.stop_thread = False

        self.position = 0
        self.data = None

        self.loaded = False
        self.paused = False
        self.active = False

        self.volume = 1.0

    def get_busy(self):
        return self.active

    def load(self, input_):
        if self.active:
            self.unload()

        try:
            self.wave = wave.open(input_, "rb")
        except EOFError:
            raise EOFError("Audio is empty. This may mean the file is corrupted.")

        self.stream = _p.open(
        format=_p.get_format_from_width(self.wave.getsampwidth()),
        channels=self.wave.getnchannels(),
        rate=self.wave.getframerate(),
        output=True)

        self.loaded = True

    def unload(self):
        if self.loaded:
            self.stop()

            self.stream.stop_stream()
            self.stream.close()
            self.wave.close()

            self.wave = None 
            self.stream = None
            self.thread = None

            self.loaded = False

    def play(self):
        self.stop_thread = False 
        self.position = 0
        self.data = None
        self.active = True

        self.wave.rewind()
        self.thread = Thread(target=self._threaded_play)

        self.thread.start()

    def _threaded_play(self):
        chunk = 2048
        data = self.wave.readframes(chunk)
        self.data = data

        while data != b'' and not self.stop_thread:

            if self.paused:
                time.sleep(0.01)
            else:
                audio = numpy.frombuffer(data, dtype=numpy.int16)

                if self.volume == 0.0:
                    audio = numpy.zeros_like(audio)
                else:
                    db = 20 * math.log10(self.volume)
                    audio = (audio * 10**(db/20)).astype(numpy.int16)
                    
                self.stream.write(audio.tobytes())
                data = self.wave.readframes(chunk)
                self.data = data

                self.position += chunk / self.wave.getframerate()

        self.active = False

    def set_volume(self, vol):
        self.volume = min(1.0, max(0.0, vol))
        
    def get_volume(self):
        return self.volume

    def get_pos(self):
        return self.position

    def stop(self):
        if self.active:
            self.stop_thread = True
            self.thread.join()
            self.position = 0
            self.data = None

    def pause(self):
        self.paused = True 

    def unpause(self):
        self.paused = False