import copy
import pyaudio
import wave
import math
import time
import numpy as np
import sys
import warnings

from threading import Thread
from io import BytesIO


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

    def get_busy(self):
        return self.active

    # def callback(in_data, frame_count, time_info, status):
    #     # based on
    #     # <https://people.csail.mit.edu/hubert/pyaudio/docs/>
    #
    #     data = self.wave.readframes(frame_count)
    #     return (data, pyaudio.paContinue)

    def refresh_devices(self):
        self.audio_devices = []  # indices must match output_device_index
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            self.audio_devices.append(copy.deepcopy(info))
            # warnings.warn("Device {}: {}".format(i, info['name']))

    def find_device_by_name(self, name):
        # for i in range(self.p.get_device_count()):
        if self.audio_devices is None:
            raise RuntimeError(
                "find_device_by_name was called before refresh_devices")
            # return -1
        for i in range(len(self.audio_devices)):
            # self.audio_devices[i] = self.p.get_device_info_by_index(i)
            # ^ Commenting this assumes refresh_devices was called
            #   before devices were added or removed.
            info = self.audio_devices[i]
            if info["name"] == name:
                if info['maxOutputChannels'] > 0:
                    return i
                else:
                    warnings.warn(
                        "Warning: preferred device '{}' is invalid"
                        " (has no output)".format(info['name']))
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
            )

        if self.stream is None:
            device_index = -1
            # List available devices
            self.refresh_devices()

            for try_name in self.preferred_device_names:
                device_index = self.find_device_by_name(try_name)
                if device_index >= 0:
                    warnings.warn("Detected {}".format(try_name))
                    break
            if device_index < 0:
                warnings.warn(
                    "No preferred device was present: {}"
                    .format(self.preferred_device_names))

            if device_index < 0:
                # If no device was present, load the first output device
                #   (may stutter and fail under pipewire+jack):
                for i in range(self.p.get_device_count()):
                    info = self.p.get_device_info_by_index(i)
                    warnings.warn("Device {}: {}".format(i, info['name']))
                    if info['maxOutputChannels'] > 0:
                        warnings.warn("- selected (first output device)")
                        # Use the first device that has output
                        device_index = i
                        break

            if device_index < 0:
                warnings.warn("Error: No suitable output device found.")
                return
            try:
                self.stream = self.p.open(
                    format=self.p.get_format_from_width(
                        self.wave.getsampwidth()
                    ),
                    channels=self.wave.getnchannels(),
                    rate=self.wave.getframerate(),
                    output=True,
                    output_device_index=device_index,
                    # stream_callback=self.callback,
                )

            except Exception as e:
                # traceback.format_exc()
                name = None
                if ((device_index >= 0)
                        and (device_index < len(self.audio_devices))):
                    name = self.audio_devices[device_index].get('name')
                print("Failed to open stream with selected device {}:"
                      " {}: {} (name={})"
                      .format(device_index,
                              type(e).__name__, e, name))
                return

        self.loaded = True

    def close(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        # print("Stopped pyaudio.", file=sys.stderr)

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
                audio = np.frombuffer(data, dtype=np.int16)

                if self.volume == 0.0 or self.muted:
                    audio = np.zeros_like(audio)
                else:
                    db = 20 * math.log10(self.volume)
                    audio = (audio * 10**(db/20)).astype(np.int16)  # noqa: E226, E501

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
