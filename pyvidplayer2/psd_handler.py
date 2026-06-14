import time
import wave
from io import BytesIO
from threading import Thread

import numpy as np
import sounddevice as sd

from .audio_handler import AudioHandler
from .error import AudioDeviceError


class PSDHandler(AudioHandler):
    def __init__(self):
        self.stream = None
        self.wave = None

        self.thread = None
        self.stop_thread = False

        self.position = 0
        self.chunks_played = 0

        self.loaded = False
        self.paused = False
        self.active = False

        self.volume = 1.0
        self.muted = False

        self.audio_devices = []
        self.preferred_device_names = [
            "pulse",
            "pipewire",
            "default",
        ]

        self._refresh_devices()
        self.device_index = self._choose_device()
        self._buffer = None

    def _refresh_devices(self):
        self.audio_devices = sd.query_devices()

    def _choose_device(self):
        for name in self.preferred_device_names:
            for i, dev in enumerate(self.audio_devices):
                if name in dev['name'].lower() and dev['max_output_channels'] > 0:
                    return i

        for i, dev in enumerate(self.audio_devices):
            if dev['max_output_channels'] > 0:
                return i

        raise AudioDeviceError("No audio devices found.")

    def _set_device_index(self, index):
        try:
            self.audio_devices[index]
        except IndexError as e:
            raise AudioDeviceError(
                f"Audio device with index {index} does not exist."
            ) from e
        self.device_index = index

    def load(self, audio_chunk):
        self.unload()

        try:
            self.wave = wave.open(BytesIO(audio_chunk), "rb")
        except EOFError as e:
            raise EOFError(
                "Audio is empty. This may mean the file is corrupted."
                " If your video has no audio track,"
                " try initializing it with no_audio=True."
                " If it has several tracks, make sure the correct one"
                " is selected with the audio_track parameter."
            ) from e

        if self.stream is None:
            # order is important
            sample_rates = [
                self.wave.getframerate(),
                int(self.audio_devices[self.device_index]["default_samplerate"])
            ]
            psd_exception = None

            for sr in sample_rates:
                try:
                    self.stream = sd.OutputStream(
                        samplerate=sr,
                        channels=self.wave.getnchannels(),
                        device=self.device_index,
                        dtype=f'int{self.wave.getsampwidth() * 8}'
                    )
                    self.stream.start()
                    break
                except sd.PortAudioError as e:
                    psd_exception = e
            else:
                raise AudioDeviceError(
                    "Failed to open audio stream with device \"{}\"".format(
                        self.audio_devices[self.device_index]["name"])
                ) from psd_exception

        self.loaded = True

    def get_num_channels(self):
        return self.audio_devices[self.device_index]["max_output_channels"]

    def play(self):
        self.stop_thread = False
        self.position = 0
        self.chunks_played = 0
        self.active = True

        self.wave.rewind()
        self.thread = Thread(target=self._threaded_play, daemon=True)
        self.thread.start()

    def _threaded_play(self):
        chunk_size = 128
        channels = self.wave.getnchannels()
        dtype_val = {1: np.int8, 2: np.int16, 4: np.int32}.get(self.wave.getsampwidth(), np.int16)

        while not self.stop_thread:
            if self.paused:
                time.sleep(0.01)
            else:
                data = self.wave.readframes(chunk_size)
                if data == b"":
                    break

                audio = np.frombuffer(data, dtype=dtype_val)

                audio = audio.reshape(-1, channels)

                if self.volume == 0.0 or self.muted:
                    audio = np.zeros_like(audio)
                elif self.volume != 1.0:
                    audio = (audio * self.volume).astype(dtype_val)

                self._buffer = audio

                # having psd bubble its exceptions clutter the stack trace
                # almost always due to handling an existing exception
                try:
                    self.stream.write(audio)
                except sd.PortAudioError:
                    break

                self.chunks_played += chunk_size
                self.position = self.chunks_played / float(self.wave.getframerate())

        self.active = False

    def stop(self):
        if self.loaded:
            self.stop_thread = True
            if self.thread and self.thread.is_alive():
                self.thread.join()
            self.position = 0
            self.chunks_played = 0

    def unload(self):
        if self.loaded:
            self.stop()
            self.wave.close()
            self.wave = None
            self.thread = None
            self.loaded = False

    def close(self):
        self.unload()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

    def set_volume(self, vol):
        self.volume = min(1.0, max(0.0, vol))

    # not ideal, should've used properties instead
    # but now the public interface is already set
    def get_volume(self):
        return self.volume

    def get_pos(self):
        return self.position

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    def get_busy(self):
        return self.active
