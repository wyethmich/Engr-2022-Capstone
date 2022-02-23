import pyaudio
import math
import struct
import wave
import time
import os
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import scipy.io.wavfile
from scipy import signal
import noisereduce as nr
from time import sleep
import socket
import soundfile as sf

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

Threshold = 150

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2

TIMEOUT_LENGTH = 3



### Change dir_num to 1, 2, 3, or 4 depending on whether you're collecting positive or negative samples for either training or testing ###
dir_num = 1

if dir_num == 1:
    f_name_directory = r'//home/pi/test_positives/'
elif dir_num == 2:
    f_name_directory = r'//home/pi/test_negatives/'
elif dir_num == 3:
    f_name_directory = r'//home/pi/train_positives/'
elif dir_num == 4:
    f_name_directory = r'//home/pi/train_negatives/'
    



class Recorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self, sample_num):
        print('\nRecording Sample #' + str(sample_num))
        rec = []
        current = time.time()
        end = current + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec), sample_num)

    def butter_highpass(self, cutoff, fs, order=5):
        nyq = 0.5*fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def butter_highpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = signal.filtfilt(b, a, data)
        return y

    def write(self, recording, sample_num):
        n_files = len(os.listdir(f_name_directory))

        filename = os.path.join(f_name_directory, str(sample_num) + ".wav")

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()

        sr, x = scipy.io.wavfile.read(filename)
        filtered = self.butter_highpass_filter(x, 2000, sr)
        scipy.io.wavfile.write(filename, sr, filtered.astype(np.int16))

        rate, data = scipy.io.wavfile.read(filename)
        reduced_noise = nr.reduce_noise(y = data, sr=rate, n_std_thresh_stationary=1.5,stationary=True)
        scipy.io.wavfile.write(filename, rate, reduced_noise.astype(np.int16))


        print('Returning to listening')
 

    def listen(self):
        i = len(os.listdir(f_name_directory))
        while True:
            
            print("\nListening beginning in:\n3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)

            state = GPIO.input(BUTTON)
            self.record(i)
            i += 1
            if not state:
                quit()
a = Recorder()

a.listen()



