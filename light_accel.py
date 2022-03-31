import time
import board
import adafruit_mpu6050
import adafruit_tsl2591
import collections
from time import sleep
from statistics import mean, stdev
import numpy as np

i2c = board.I2C()
mpu=adafruit_mpu6050.MPU6050(i2c)
light=adafruit_tsl2591.TSL2591(i2c)

BUF_LEN = 20 #seconds
STD_COEF = 2.5

buf = collections.deque(maxlen=BUF_LEN*10)
buf.append(mean(mpu.acceleration))
time.sleep(0.1)
buf.append(mean(mpu.acceleration))

for i in range(BUF_LEN*10):
        buf.append(np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2)))
        time.sleep(0.1)
while True:
    #print("Lux: " + str(round(light.lux, 1)) + "    Accel Mag Diff: %f m/s^2" %% (mean(buf) - np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2))))
    #print(str(1.5 * stdev(buf)))
    magnitude = np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2))
    #print(stdev(buf), abs(mean(buf) - magnitude))
    if abs(mean(buf) - magnitude) > (STD_COEF * stdev(buf)):
        print("Spike: %f m/s^2" % abs(mean(buf) - magnitude))
    else:
        buf.append(magnitude)
    #print(mean(buf))
    #print( str(np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2))))
    time.sleep(0.1)

