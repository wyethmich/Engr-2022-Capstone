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


UDP_IP = "140.182.152.76"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
success = None
#while success is None:
#    try:
#        success = sock.bind((UDP_IP, UDP_PORT))
#    except:
#        print("Error")
#        pass
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.5)
BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)


with picamera.PiCamera() as camera:
  camera.resolution = (1640, 1232)
  camera.framerate=30
  stream = picamera.PiCameraCircularIO(camera, seconds=20, bitrate=15*1000000)
  camera.start_recording(stream, format='h264', profile='high', level='4.2')
  
  try:
    while True:
      camera.wait_recording(0.5)
      #print("Waiting...")
      try:
        data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
      except:
        data = 0
        pass
      #state = GPIO.input(BUTTON)
      print("Data: ", data)
      if data == b'1':# or not state:
        print('Motion detected!')
        data = 0
        camera.wait_recording(10)
        stream.copy_to('final.h264', seconds=20)
        stream.clear()

        date = datetime.now().strftime("%m.%d.%Y_%H:%M:%S")
        command = "MP4Box -add final.h264 ~/Engr-2022-Capstone/camera/videos/" + date + ".mp4"

        call([command], shell=True)
        os.remove('final.h264')
        print("vid conv")
  except:
      camera.stop_recording()
      camera.close()
  finally:
      camera.stop_recording()
      camera.close()
