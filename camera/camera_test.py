import io
import os
import random
import picamera
from PIL import Image
import RPi.GPIO as GPIO
import time
import socket
from subprocess import call
from datetime import datetime


UDP_IP = "10.20.14.106"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DRAGM)
sock.bind((UDP_IP, UDP_PORT))

while True:
  data, addr = sock.recvfrom(1024)
  print("received message: %s" % data)

BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

def write_video(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it
    # simultaneously
    with io.open('before.h264', 'wb') as output:
      for frame in stream.frames:
        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
          stream.seek(frame.position)
          break
      while True:
        buf = stream.read1()
        if not buf:
          break
        output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()

with picamera.PiCamera() as camera:
  camera.resolution = (1280, 720)
  stream = picamera.PiCameraCircularIO(camera, seconds=10)
  camera.start_recording(stream, format='h264')
  try:
    while True:
      camera.wait_recording(1)
      print("Waiting...")
      state = GPIO.input(BUTTON)
      if not state:
        print('Motion detected!')
        # As soon as we detect motion, split the recording to
        # record the frames "after" motion
        camera.split_recording('after.h264')
        # Write the 10 seconds "before" motion to disk as well
        write_video(stream)
        # Wait until motion is no longer detected, then split
        # recording back to the in-memory circular buffer
        camera.wait_recording(10)
        print('Motion stopped!')
        camera.split_recording(stream)

        command1 = "ffmpeg -f concat -safe 0 -i mylist.txt -c copy final.h264"
        date = datetime.now().strftime("%m.%d.%Y_%H:%M:%S")
        command2 = "MP4Box -add final.h264 ~/Engr-2022-Capstone/camera/videos/" + date + ".mp4"

        call([command1], shell=True)
        call([command2], shell=True)
        os.remove('before.h264')
        os.remove('after.h264')
        os.remove('final.h264')
        print("vid conv")
  finally:
      camera.stop_recording()

  
