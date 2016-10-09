
import pyaudio
import time
import numpy as np
import scipy.signal as signal
import audioop as ap
import curses
from matplotlib import pyplot as plt

WIDTH = 2
CHANNELS = 2
RATE = 44100
p = pyaudio.PyAudio()

class audioProcessor:
    def __init__(self):
        self.recording = False
        self.playingBack = False
        self.loop = []
        self.loopIndex = 0

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
        print 'Recording ', self.recording
        # print 'Playing loop ', self.playingBack
        if in_data and not self.playingBack:
            decoded = self.processSound(in_data)
            result_waiting = True
        elif self.playingBack:
            if self.loop:
                if self.loopIndex > len(self.loop) - 1:
                    self.loopIndex = 0
                decoded = self.loop[self.loopIndex]
                self.loopIndex += 1
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
window = curses.initscr()
# window.nodelay(1)
while stream.is_active():
    ch = window.getch()
    if ch == 10:
        ap.recording = not ap.recording
        if ap.recording:
            'Recording'
            ap.playingBack = False
        elif ap.loop:
            ap.playingBack = True
    # time.sleep(0.1)


stream.stop_stream()
stream.close()

p.terminate()
