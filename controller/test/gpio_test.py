import cv2
import numpy as np
import datetime
import time

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H



FT232H.use_FT232H()

ft232h = FT232H.FT232H()
# Configure digital inputs and outputs using the setup function.
# Note that pin numbers 0 to 15 map to pins D0 to D7 then C0 to C7 on the board.
ft232h.setup(7, GPIO.IN)   # Make pin D7 a digital input.
ft232h.setup(8, GPIO.OUT)  # Make pin C0 a digital output.
ft232h.setup(9, GPIO.OUT)
ft232h.setup(10, GPIO.OUT)
ft232h.setup(11, GPIO.OUT)
ft232h.setup(12, GPIO.OUT)


#camera fix
# sudo nano /etc/environment
# QT_X11_NO_MITSHM=1

def send_command(value):

    while ft232h.input(7) == GPIO.HIGH: # READY FLAG FROM ROBO
        time.sleep(.100)

    ft232h.output(11, GPIO.HIGH if (value >> 3) % 2 == 1 else GPIO.LOW)
    ft232h.output(10, GPIO.HIGH if (value >> 2) % 2 == 1 else GPIO.LOW)
    ft232h.output(9, GPIO.HIGH if (value >> 1) % 2 == 1 else GPIO.LOW)
    ft232h.output(8, GPIO.HIGH if value % 2 == 1 else GPIO.LOW)
    time.sleep(.100)
    print "COMMAND: {}".format(value)

    ft232h.output(12, GPIO.HIGH) # ENABLE FLAG = 1
    print "enable = 1"

    while ft232h.input(7) == GPIO.LOW: # READY FLAG FROM ROBO
        time.sleep(.100)
    ft232h.output(12, GPIO.LOW) # ENABLE FLAG = 0
    print "enable = 0"

    ft232h.output(11, GPIO.LOW)
    ft232h.output(10, GPIO.LOW)
    ft232h.output(9, GPIO.LOW)
    ft232h.output(8, GPIO.LOW)



#send_command(0b0001) # TURN RIGHT
#send_command(0b0010) # TURN LEFT
#send_command(0b0011) # 180
#send_command(0b0100) # r2t
while 42:
    send_command(0b0101) # l2t
#send_command(0b0110) # f2t
#send_command(0b0111) # b2t
#send_command(0b1011) # foto start
