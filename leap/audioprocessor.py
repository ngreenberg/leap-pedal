import pyaudio
import time
import numpy as np
import scipy.signal as signal
import audioop as ap
import curses
from scikits.samplerate import resample
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
        self.recordingLoop = []
        self.loopIndex = 0

    # def pitchShift(self, sample):


    def processSound(self, in_data):
        decoded = np.fromstring(in_data, dtype=np.float32)
        # if reversing:
        #     decoded = ap.reverse(decoded, 4)
        if self.recording:
            self.recordingLoop.append(decoded)
        return decoded

    def callback(self, in_data, frame_count, time_info, status):
        global decoded
        global result_waiting
        # print 'Recording ', self.recording
        if in_data and not self.playingBack:
            decoded = self.processSound(in_data)
            result_waiting = True
        elif self.playingBack:
            if self.recording:
                self.recordingLoop.append(np.fromstring(in_data, dtype=np.float32))
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
