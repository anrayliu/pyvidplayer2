import copy
import pyaudio
import wave
import math
import time
import numpy as np
from threading import Thread
from io import BytesIO
from .error import *


class PyaudioHandler:
    """A simple wrapper for PyAudio to play streams from memory.

    Attributes:
        audio_devices (list[dict]): A list of audio devices where
            the index is a valid value for the output_device_index
            argument of self.p.open.
        preferred_device_names (list[str]): A list of audio device names
            that are preferred and will only be used if one exists (in
            order from most to least preferred). If none is found, the
            first output device will be used (Stutters and works only
            intermittently on Ubuntu Studio with pipewire+jack).
            NOTE: The "jack" device can only use a specific sample rate,
            otherwise "Failed to open stream with selected device 13:
            OSError: [Errno -9997] Invalid sample rate (name=jack)"
            occurs in self.stream.write.
        stream (pyaudio.PyAudio.Stream): The open audio device's output
            stream obtained by self.p.open(...).
    """

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

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_devices = []
        self.preferred_device_names = [
            "pulse",
            "pipewire",  # pipewire stutters with jack on Ubuntu Studio 24.04
            #  (sample rate related? but QSynth stutters if pipewire is
            #  selected with 48000 Hz sample rate matching jack)
            "default",  # no sound & freezes on Ubuntu Studio 24.04
            # "sysdefault",  # not an output device
        ]
        self.device_index = self.choose_device()

        self._buffer = None # used for testing purposes

    def _set_device_index(self, index):
        try:
            self.audio_devices[index]
        except IndexError:
            raise AudioDeviceError(f"Audio device with index {index} does not exist.")
        else:
            self.device_index = index

    def get_busy(self):
        return self.active

    # def callback(in_data, frame_count, time_info, status):
    #     # based on
    #     # <https://people.csail.mit.edu/hubert/pyaudio/docs/>
    #
    #     data = self.wave.readframes(frame_count)
    #     return (data, pyaudio.paContinue)

    def choose_device(self):
        device_index = -1
        # List available devices
        self.refresh_devices()

        for try_name in self.preferred_device_names:
            device_index = self.find_device_by_name(try_name)
            if device_index != -1:
                # warnings.warn("Detected {}".format(try_name))
                break
        # if device_index < 0:
        # warnings.warn(
        #    "No preferred device was present: {}"
        #    .format(self.preferred_device_names))

        if device_index < 0:
            # If no device was present, load the first output device
            #   (may stutter and fail under pipewire+jack):
            for i, info in enumerate(self.audio_devices):
                if info["maxOutputChannels"] > 0:
                    # warnings.warn("- selected (first output device)")
                    device_index = i
                    break

        if device_index < 0:
            raise AudioDeviceError("No audio devices found.")

        return device_index

    def refresh_devices(self):
        self.audio_devices = []  # indices must match output_device_index
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            self.audio_devices.append(copy.deepcopy(info))
            
            # warnings.warn("Device {}: {}".format(i, info['name']))

    def find_device_by_name(self, name):
        if self.audio_devices is None:
            raise RuntimeError("find_device_by_name was called before refresh_devices")
        for i in range(len(self.audio_devices)):
            # self.audio_devices[i] = self.p.get_device_info_by_index(i)
            # ^ Commenting this assumes refresh_devices was called
            #   before devices were added or removed.
            info = self.audio_devices[i]
            if info["name"] == name:
                if info['maxOutputChannels'] > 0:
                    return i
                #else:
                #    warnings.warn(
                #        "Warning: preferred device '{}' is invalid"
                #        " (has no output)".format(info['name']))
        return -1

    def load(self, bytes_):
        self.unload()
        try:
            self.wave = wave.open(BytesIO(bytes_), "rb")
        except EOFError:
            raise EOFError(
                "Audio is empty. This may mean the file is corrupted."
                " If your video has no audio track,"
                " try initializing it with no_audio=True."
                " If it has several tracks, make sure the correct one"
                " is selected with the audio_track parameter."
            )

        if self.stream is None:
            try:
                self.stream = self.p.open(
                    format=self.p.get_format_from_width(
                        self.wave.getsampwidth()
                    ),
                    channels=self.wave.getnchannels(),
                    rate=self.wave.getframerate(),
                    output=True,
                    output_device_index=self.device_index,
                    # stream_callback=self.callback,
                )

            except:
                raise AudioDeviceError("Failed to open audio stream with device \"{}.\"".format(self.audio_devices[self.device_index]["name"]))
                
        self.loaded = True

    def get_num_channels(self):
        return self.audio_devices[self.device_index]["maxOutputChannels"]

    def close(self):
        if self.stream is not None:
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
        self.chunks_played = 0
        self.active = True

        self.wave.rewind()
        self.thread = Thread(target=self._threaded_play, daemon=True)

        self.thread.start()

    def _threaded_play(self):
        CHUNK_SIZE = 128 #increasing this will reduce get_pos precision

        while not self.stop_thread:
            if self.paused:
                time.sleep(0.01)
            else:
                data = self.wave.readframes(CHUNK_SIZE)
                if data == b"":
                    break

                audio = np.frombuffer(data, dtype=np.int16)

                if self.volume == 0.0 or self.muted:
                    audio = np.zeros_like(audio)
                else:
                    db = 20 * math.log10(self.volume)
                    audio = (audio * 10 ** (db / 20)).astype(np.int16)  # noqa: E226, E501

                self._buffer = audio

                self.stream.write(audio.tobytes())

                self.chunks_played += CHUNK_SIZE
                self.position = self.chunks_played / float(self.wave.getframerate())

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
            self.chunks_played = 0

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False
