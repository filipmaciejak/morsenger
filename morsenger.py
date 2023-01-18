#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import board
import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
from datetime import datetime
import neopixel
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import sqlite3

# //////////////////////// beginning of config
# pin numbers in BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led1 = 13
led2 = 12
led3 = 19
led4 = 26
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
GPIO.setup(led4, GPIO.OUT)

buttonRed = 5
buttonGreen = 6
encoderLeft = 17
encoderRight = 27
GPIO.setup(buttonRed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonGreen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoderLeft, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoderRight, GPIO.IN, pull_up_down=GPIO.PUD_UP)

buzzerPin = 23
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.output(buzzerPin, 1)

ws2812pin = 8
# /////////////////////////////// end of config

text = ""
chatMode = True
noEscape = True
morseCode = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
             'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
             'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
             'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
             '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
             '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', 'ą': '.-.-', 'ć': '-.-..',
             'ę': "..--..", 'ł': '.-..-', 'ń':  '--.--', 'ó': '---.', 'ś': '...--...', 'ż': '--..-.', 'ź': '--.-'}
# TODO: zmienić słownik na taki, którego kluczem jest string kropek i kresek, a wartością litera

# The terminal ID - can be any string.
terminal_id = "T0"
# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

client = mqtt.Client()


# Thw main window with buttons to simulate the RFID card usage.
# window = tkinter.Tk()

def send_message(message):
    client.publish("message", str(message) + "." + terminal_id, )


def process_message(client, userdata, message):
    connention = sqlite3.connect("messages.db")
    cursor = connention.cursor()
    cursor.execute("INSERT INTO messages_log VALUES (?, ?)",
    (str(message.payload.decode('utf-8')), 1))
    connention.commit()
    connention.close()

    print('RFID scan: ' + str(message.payload.decode('utf-8')))


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


def rfidRead():
    MIFAREReader = MFRC522()
    while noEscape:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i * 8)
                    # TODO: num może być nickiem sendera
                # timesta,p = time.time()
                # # if timestamp-last
                # now = datetime.now().time()  # time object
                # time.sleep(0.5)
                # # buzzer
                # GPIO.output(buzzerPin, not True)
                # time.sleep(1)
                # GPIO.output(buzzerPin, not False)
                # TODO: zrobić coś żeby buzzer nie szalał

                global text, chatMode
                print(text)
                send_message(text)
                text = ""
                chatMode = True


def load_chat():
    pass
    # TODO: wczytaj chat z bazy danych i wypisz ją na okienku


def show_chat():
    global chatMode
    chatMode = True
    pass
    # TODO: włącz widok chatu, będzie można scrollować


def show_message():
    global chatMode, text
    chatMode = False

    disp = SSD1331.SSD1331()

    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    # Create blank image for drawing.
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    fontLarge = ImageFont.truetype('./lib/oled/Font.ttf', 20)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

    # print("- draw rectangle")
    draw.rectangle([(5, 5), (90, 30)], fill="BLUE")

    # print("- draw morse")
    draw.text((8, 0), text, font=fontSmall, fill="BLACK")
    # print("- draw symbol")
    draw.text((12, 40), 'World !!!', font=fontSmall, fill="BLACK")

    # image1 = image1.rotate(45)
    disp.ShowImage(image1, 0, 0)
    time.sleep(2)

    # disp.clear()
    # disp.reset()


def scroll_up(channel):
    if chatMode:
        pass
        # TODO: scrolluj w górę


def scroll_down(channel):
    if chatMode:
        pass
        # TODO: scrolluj w dół


def green_start(channel):
    global text
    text = text + "."
    show_message()


def red_start(channel):
    global text
    text = text + "-"
    show_message()


def init():
    # save time of pressing the button
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=green_start, bouncetime=200)
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=red_start, bouncetime=200)

    # # save time of releasing the button
    # TODO: optionally enable
    # GPIO.add_event_detect(buttonGreen, GPIO.RISING, callback = green_stop, bouncetime = 100)
    # GPIO.add_event_detect(buttonRed, GPIO.RISING, callback = red_stop, bouncetime = 100)

    # scroll the chat view
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=scroll_down, bouncetime=100)
    GPIO.add_event_detect(encoderRight, GPIO.FALLING, callback=scroll_up, bouncetime=100)

    connect_to_broker()

    # receiver code
    client.on_message = process_message
    client.loop_start()
    client.subscribe('message')

    rfidRead()

    disconnect_from_broker()


if __name__ == "__main__":
    init()
