
import pyaudio
import time
import numpy as np
import scipy.signal as signal
import audioop as ap
from matplotlib import pyplot as plt

WIDTH = 2
CHANNELS = 2
RATE = 44100
p = pyaudio.PyAudio()

class audioProcessor:
    def __init__(self):
        self.recording = True
        self.playingBack = False
        self.loop = []
        self.repeatingLoop = []

    def processSound(self, in_data):
        decoded = np.fromstring(in_data, dtype=np.float32)
        # if reversing:
        #     decoded = ap.reverse(decoded, 4)
        if self.recording:
            self.loop.append(decoded)
        return decoded

    def callback(self, in_data, frame_count, time_info, status):
        global decoded
        global result_waiting
        if(len(self.loop) > 75):
            self.recording = False
            self.playingBack = True
        if in_data and not self.playingBack:
            decoded = self.processSound(in_data)
            result_waiting = True
        elif self.playingBack:
            if self.repeatingLoop:
                decoded = self.repeatingLoop.pop(0)
                self.loop.append(decoded)
            elif self.loop:
                decoded = self.loop.pop(0)
                self.repeatingLoop.append(decoded)
            else:
                self.playingBack = False
        else:
            print('no input')
        return (decoded, pyaudio.paContinue)

ap = audioProcessor()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                stream_callback=ap.callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)


stream.stop_stream()
stream.close()

p.terminate()
