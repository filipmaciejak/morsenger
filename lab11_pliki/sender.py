#!/usr/bin/env python3

import time
import buzzer
import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
import board
import neopixel
import paho.mqtt.client as mqtt
from datetime import datetime

broker = "localhost"
client = mqtt.Client()

def buzz():
    #pixels = neopixel.NeoPixel(
       # board.D18, 8, brightness=1.0/32, auto_write=False)

    #pixels.fill((0, 255, 0))
    #pixels.show()
    setLeds(True)
    buzzer.buzzer(True)
    time.sleep(0.1)
    #pixels.fill((0, 0, 0))
    #pixels.show()
    setLeds(False)
    buzzer.buzzer(False) # pylint: disable=no-member

def setLeds(isGood):
    GPIO.output(led1, isGood)
    GPIO.output(led2, isGood)
    GPIO.output(led3, isGood)
    GPIO.output(led4, isGood)

def main():
    client.connect(broker)
    reads=[]
    MIFAREReader = MFRC522()
    lastRead = time.time()
    while True:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i*8)
                timestamp = time.time()
                if(timestamp - lastRead) >= 0.5:
                    buzz()
                    print(f"Card read UID: {uid} > {num}")
                    reads.append([num, datetime.fromtimestamp(timestamp)])
                    client.publish('rfid/records', str(reads[-1][0]) + ' on ' + str(reads[-1][1]))
                lastRead = time.time()
                

if __name__ == "__main__":
    main()