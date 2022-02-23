import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment

def normalize_dirs():
    dirs = [r'//home/pi/test_positives', r'//home/pi/test_negatives']
    for dir_path in dirs:
        for filename in os.listdir(dir_path):
            normalize_files(dir_path + "/" + filename)
def normalize_files(f):
        data, sr = sf.read(f)
        temp = data[(sr*3):]
        
        diff = (sr * 4) - len(temp)
        if diff < 0:
            temp  = data[:-(sr*4)]
        else:
            temp = np.append(temp, [0]*diff)
        sf.write(f[:-4]+"_padded.wav", temp, sr)
        os.remove(f)
#normalize_files(r'//home/pi/pos_sample.wav')
