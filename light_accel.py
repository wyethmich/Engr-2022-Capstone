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


buf = collections.deque(maxlen=36000)
buf.append(mean(mpu.acceleration))
time.sleep(0.1)
buf.append(mean(mpu.acceleration))


while True:
    #print("Lux: " + str(round(light.lux, 1)) + "    Accel Mag Diff: %f m/s^2" % (mean(buf) - mean(mpu.acceleration)))
    #print(str(1.5 * stdev(buf)))
    #if (mean(buf) - mean(mpu.acceleration)) > (1.2 * stdev(buf)):
    #    print("Spike: %f m/s^2" % (mean(buf) - mean(mpu.acceleration)))
    #buf.append(mean(mpu.acceleration))
    print( str(np.sqrt((mpu.acceleration[0] ** 2) + (mpu.acceleration[1] ** 2) + (mpu.acceleration[2] ** 2)))) 
    time.sleep(0.1)
