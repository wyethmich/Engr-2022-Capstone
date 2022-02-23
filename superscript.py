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
from joblib import dump, load
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import MidTermFeatures as aF
import statistics
import board
import adafruit_tsl2591
import adafruit_mpu6050
from statistics import mean, stdev
import collections


#time.sleep(60)  
UDP_IP = "140.182.152.68"

UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP

sock.settimeout(1)

# 129 86 model
model = r'//home/pi/Engr-2022-Capstone/svmthings/trained_models/0.91_129_86_svc.joblib'
cl = load(model) 
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

f_name_directory = r'//home/pi/Engr-2022-Capstone/audioconfig/audiotests/live_demo'

i2c = board.I2C()
light=adafruit_tsl2591.TSL2591(i2c)
mpu = adafruit_mpu6050.MPU6050(i2c)

mpu_buf = collections.deque(maxlen=36000)
mpu_buf.append(np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2)))
time.sleep(0.1)
mpu_buf.append(np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2)))

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

    def print_bird(self, val):
        if val == 1:        
            print("      \.\ \n\
     _.\.\_\n\
    /      \ \n\
   /  o _ o \ \n\
   (    \/  )\n\
  )          (\n\
(    -  -  -  )\n\
(             )\n\
 (            )\n\
  [          ]\n\
---/l\    /l\--------\n\
  ----------------\n\
     (  )\n\
    ( __ _)\n")



        if val == 0:
            print("__    \.\       __ \n\
\ \  _.\.\_    / /\n\
 \ \/      \  / /\n\
  \ \ o _ o \/ / \n\
   \ \  \/  / / \n\
  ) \ \    / / \n\
(    \ \- /-/ ) \n\
(     \ \/ /  ) \n\
 (    / /\ \  ) \n\
  [  / /  \ \] \n\
---//\/   /\ \------- \n\
  -/-/------\-\--- \n\
  / / (  )   \ \ \n\
 /_/ ( __ _)  \_\ \n")





    def record(self):
        print('Noise detected, classifying.....')
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
        text = model.split("_")
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
        reduced_noise = nr.reduce_noise(y = data, sr=rate, n_std_thresh_stationary=1.5,stationary=True)
        scipy.io.wavfile.write(filename, rate, reduced_noise.astype(np.int16))        

        fs, s = aIO.read_audio_file(filename)
        mt, st, mt_n = aF.mid_feature_extraction(s, fs, 1 * fs, 1 * fs, 0.05 * fs, 0.05 * fs)
        features = [statistics.mean(mt[int(text[2])]), statistics.mean(mt[int(text[3])])]
        
        pred = cl.predict([features])
        if pred == 1 or pred == 0:
            print("Bird!")
            print("Recording Data...")
            sock.sendto(str.encode("1"), (UDP_IP, UDP_PORT))
            lux = light.lux
            with open('bird_log.txt', 'a') as fd:
                fd.write(f"\n{date}: " + str(lux))
                
            self.print_bird(1)
            
        else:
            print("Not a bird!")
            print("No data recorded")
            self.print_bird(0)
            os.remove(filename)
    
        print('Returning to listening')
    


    def listen(self):
        i = 0
        print('Listening beginning')
        while True:
            state = GPIO.input(BUTTON)
            input = self.stream.read(chunk,exception_on_overflow = False)
            rms_val = self.rms(input)

            mag = np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2))
            #print(str(mean(mpu_buf) - mag) + " " + str(stdev(mpu_buf) * 2))
            if rms_val > Threshold:
                if (mean(mpu_buf) - mag) > stdev(mpu_buf) * 2:
                    self.record()
            if not state:
                quit()
a = Recorder()

a.listen()
