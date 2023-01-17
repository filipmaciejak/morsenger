#!/usr/bin/env python3

#sender

import paho.mqtt.client as mqtt
import tkinter
import time
import board
import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
from datetime import datetime
import neopixel

noEscape = True

# The terminal ID - can be any string.
terminal_id = "T0"
# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()

# Thw main window with buttons to simulate the RFID card usage.
# window = tkinter.Tk()

def send_message(message):
    client.publish("card/name", str(message) + "." + terminal_id,)

# def rfidRead():
#     MIFAREReader = MFRC522()
#     cards = {}
#     pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)
#     while noEscape:
#         (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
#         if status == MIFAREReader.MI_OK:
#             (status, uid) = MIFAREReader.MFRC522_Anticoll()
#             if status == MIFAREReader.MI_OK:
#                 num = 0
#                 for i in range(0, len(uid)):
#                     num += uid[i] << (i*8)
#                 if cards.get(num) is None:
                
#                     send_message(num)
                    
#                     pixels[0] = (0, 255, 0)
#                     pixels[1] = (0, 255, 0)
#                     pixels[2] = (0, 255, 0)
#                     pixels[3] = (0, 255, 0)
#                     pixels[4] = (0, 255, 0)
#                     pixels[5] = (0, 255, 0)
#                     pixels[6] = (0, 255, 0)
#                     pixels[7] = (0, 255, 0)
#                     pixels.show()
                    
#                     now = datetime.now().time() # time object
# #                    print(f"Card read UID: {uid} > {num}")
# #                    print(f"at time: {now}")
#                     cards[num] = now
                    
#                     #buzzer
#                     GPIO.output(buzzerPin, not True)
#                     time.sleep(1)
#                     GPIO.output(buzzerPin, not False)
                    
#                     pixels[0] = (0, 0, 0)
#                     pixels[1] = (0, 0, 0)
#                     pixels[2] = (0, 0, 0)
#                     pixels[3] = (0, 0, 0)
#                     pixels[4] = (0, 0, 0)
#                     pixels[5] = (0, 0, 0)
#                     pixels[6] = (0, 0, 0)
#                     pixels[7] = (0, 0, 0)
#                     pixels.show()

def connect_to_broker():
    # Connect to the broker.
    client.connect(broker)
    # Send message about conenction.
    send_message("Client connected")

def disconnect_from_broker():
    # Send message about disconenction.
    send_message("Client disconnected")
    # Disconnet the client.
    client.disconnect()

def escape(channel):
    global noEscape
    noEscape=False

# def run_sender():
#     connect_to_broker()
    
#     GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback = escape, bouncetime = 200)
#     print('Place the card close to the reader (on the right side of the set).')
#     rfidRead()

#     disconnect_from_broker()

def rfidRead():
    MIFAREReader = MFRC522()
    while noEscape:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i*8)
                    # TODO: num może być nickiem sendera
                # send_message(num)

                # pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)
                # pixels[0] = (0, 255, 0)
                # pixels[1] = (0, 255, 0)
                # pixels[2] = (0, 255, 0)
                # pixels[3] = (0, 255, 0)
                # pixels[4] = (0, 255, 0)
                # pixels[5] = (0, 255, 0)
                # pixels[6] = (0, 255, 0)
                # pixels[7] = (0, 255, 0)
                # pixels.show()

                
                # timesta,p = time.time()

                # if timestamp-last
                now = datetime.now().time() # time object
                time.sleep(0.5)
                #buzzer
                GPIO.output(buzzerPin, not True)
                time.sleep(1)
                GPIO.output(buzzerPin, not False)
                
                global text
                print(text)
                text = ""
                
                # pixels[0] = (0, 0, 0)
                # pixels[1] = (0, 0, 0)
                # pixels[2] = (0, 0, 0)
                # pixels[3] = (0, 0, 0)
                # pixels[4] = (0, 0, 0)
                # pixels[5] = (0, 0, 0)
                # pixels[6] = (0, 0, 0)
                # pixels[7] = (0, 0, 0)
                # pixels.show()

def load_chat():
    pass
    # TODO: wczytaj chat z bazy danych i wypisz ją na okienku

def show_chat():
    pass
    # TODO: włącz widok chatu, będzie można scrollować
 
def show_message():
    pass
    # TODO: włącz widok pisania wiadomości, nie będzie można scrollować

def scroll_up(channel):
    pass
    # TODO: scrolluj w górę

def scroll_down(channel):
    pass
    # TODO: scrolluj w dół

# greenTime = 0
# redTime = 0
text = ""

def green_start(channel):
    global text
    text = text + "."
    show_message()

def red_start(channel):
    global text
    text = text + "-"
    show_message()

# def green_stop(channel):
#     print(datetime.now().time())

# def red_stop(channel):
#     pass
#     # TODO: save time


def init():    
    # save time of pressing the button
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback = green_start, bouncetime = 200)
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback = red_start, bouncetime = 200)

    # # save time of releasing the button
    # GPIO.add_event_detect(buttonGreen, GPIO.RISING, callback = green_stop, bouncetime = 100)
    # GPIO.add_event_detect(buttonRed, GPIO.RISING, callback = red_stop, bouncetime = 100)

    # scroll the chat view
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback = scroll_down, bouncetime = 100)
    GPIO.add_event_detect(encoderRight, GPIO.FALLING, callback = scroll_up, bouncetime = 100)

    connect_to_broker()

    rfidRead()

if __name__ == "__main__":
    init()
    # run_sender()
