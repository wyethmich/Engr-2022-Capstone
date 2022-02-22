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

#time.sleep(60)  
UDP_IP = "140.182.152.20"

UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(1)




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

TIMEOUT_LENGTH = 2

f_name_directory = r'//home/pi/audioconfig/audiotests/decaudio'

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
   
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))
        
        date = datetime.now().strftime("%m|%d-%H:%M:%S")
        filename = os.path.join(f_name_directory,'{}.wav'.format(date))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()

        sr, x = scipy.io.wavfile.read(filename)
        b = signal.firwin(101, cutoff=500, fs=sr, pass_zero=False)
        x = signal.lfilter(b, [1.0], x)
        scipy.io.wavfile.write(filename, sr, x.astype(np.int16))        

        rate, data = scipy.io.wavfile.read(filename)
        #reduced_noise = nr.reduce_noise(y=data, sr=rate)
        reduced_noise = nr.reduce_noise(y = data, sr=rate, n_std_thresh_stationary=1.5,stationary=True)
        scipy.io.wavfile.write(filename, rate, reduced_noise.astype(np.int16))        

    
        print('Returning to listening')
    


    def listen(self):
        i = 0
        print('Listening beginning')
        while True:
            state = GPIO.input(BUTTON)
            input = self.stream.read(chunk,exception_on_overflow = False)
            rms_val = self.rms(input)
            print(rms_val)
            if rms_val > Threshold:# and data == 1:
                try:
                    data, addr = sock.recvfrom(1024)
                    print(data)
                except socket.timeout as e:
                    err = e.args[0]
                    if err == 'timed out':
                        sleep(1)
                        print('Timed out')
                        continue
                    else:
                        print(e)
                        sys.exit(1)
                else:
                    data = int(data)
                    #print(data)
                    if data == 1:
                        self.record()
                    print("both checks met!")
            if not state:
                quit()
a = Recorder()

a.listen()
