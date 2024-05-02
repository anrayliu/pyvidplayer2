import pyaudio
import wave
import math 
import time
import numpy
from threading import Thread
from io import BytesIO


class PyaudioHandler:
    def __init__(self) -> None:
        self.stream = None
        self.wave = None

        self.thread = None
        self.stop_thread = False

        self.position = 0

        self.loaded = False
        self.paused = False
        self.active = False

        self.volume = 1.0
        self.muted = False

        self.p = pyaudio.PyAudio()
        self.stream = None 

    def get_busy(self):
        return self.active

    def load(self, bytes):
        self.unload()

        try:
            self.wave = wave.open(BytesIO(bytes), "rb")
        except EOFError:
            raise EOFError("Audio is empty. This may mean the file is corrupted or that the video does not contain any audio.")

        if self.stream is None:
            self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wave.getsampwidth()),
            channels=self.wave.getnchannels(),
            rate=self.wave.getframerate(),
            output=True)

        self.loaded = True

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def unload(self):
        if self.loaded:
            self.stop()

            self.wave.close()

            self.wave = None 
            self.thread = None

            self.loaded = False

    def play(self):
        self.stop_thread = False 
        self.position = 0
        self.active = True

        self.wave.rewind()
        self.thread = Thread(target=self._threaded_play)

        self.thread.start()

    def _threaded_play(self):
        chunk = 2048
        data = self.wave.readframes(chunk)

        while data != b'' and not self.stop_thread:

            if self.paused:
                time.sleep(0.01)
            else:
                audio = numpy.frombuffer(data, dtype=numpy.int16)

                if self.volume == 0.0 or self.muted:
                    audio = numpy.zeros_like(audio)
                else:
                    db = 20 * math.log10(self.volume)
                    audio = (audio * 10**(db/20)).astype(numpy.int16)
                    
                self.stream.write(audio.tobytes())
                data = self.wave.readframes(chunk)

                self.position += chunk / self.wave.getframerate()

        self.active = False

    def set_volume(self, vol):
        self.volume = min(1.0, max(0.0, vol))
        
    def get_volume(self):
        return self.volume

    def get_pos(self):
        return self.position

    def stop(self):
        if self.loaded:
            self.stop_thread = True
            self.thread.join()
            self.position = 0

    def pause(self):
        self.paused = True 

    def unpause(self):
        self.paused = False

    def mute(self):
        self.muted = True 

    def unmute(self):
        self.muted = False 