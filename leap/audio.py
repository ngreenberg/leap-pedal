
import pyaudio
import time
import numpy as np
import scipy.signal as signal
import audioop as ap
from matplotlib import pyplot as plt


WIDTH = 2
CHANNELS = 2
RATE = 44100
loop = []
recording = False
playingBack = False
p = pyaudio.PyAudio()

def processSound(in_data):
    decoded = np.fromstring(in_data, dtype=np.float32)
    if reversing:
        decoded = ap.reverse(decoded, 4)
    if recording:
        loop.append(decoded)

def callback(in_data, frame_count, time_info, status):
    global decoded
    global result_waiting
    if in_data and not playingBack:
        processSound(in_data)
        result_waiting = True
    else if playingBack:
        ## ???
    else:
        print('no input')

    return (decoded, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)


stream.stop_stream()
stream.close()

p.terminate()
