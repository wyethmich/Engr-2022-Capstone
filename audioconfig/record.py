import pyaudio
import wave
import os
import sys
from array import array 
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 1 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 1  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = input("How long would you like to record (sec): ")
RECORD_SECONDS = int(RECORD_SECONDS)
#WAVE_OUTPUT_FILENAME = "output.wav"
WAVE_OUTPUT_FILENAME = raw_input("name file: ")
save_path = '//home/pi/audioconfig/audiotests'
completeName = os.path.join(save_path, WAVE_OUTPUT_FILENAME) 
p = pyaudio.PyAudio()
 
stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            input_device_index=RESPEAKER_INDEX,)
 
print("* recording")
 
frames = []
 
for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    
    frames.append(data)
    data_chunk = array('h',data)
    vol = max(data_chunk)
#    frames.append(data) 
    print("\n") 
print("* done recording")
 
stream.stop_stream()
stream.close()
p.terminate()
 
wf = wave.open(completeName, 'wb')
wf.setnchannels(RESPEAKER_CHANNELS)
wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf.setframerate(RESPEAKER_RATE)
wf.writeframes(b''.join(frames))
wf.close()

