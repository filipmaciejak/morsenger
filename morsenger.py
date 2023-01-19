#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import board
import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
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
morseCode = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
             '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
             '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
             '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5',
             '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0', '--..--': ', ', '.-.-.-': '.',
             '..--..': '?', '-..-.': '/', '-....-': '-', '-.--.': '(', '-.--.-': ')', '.-.-': 'Ą', '-.-..': 'Ć',
             "..--..": 'Ę', '.-..-': 'Ł', '--.--': 'Ń', '---.': 'Ó', '...--...': 'Ś', '--..-.': 'Ż', '--.-': 'Ź'}
pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)

# The terminal ID - can be any string.
terminal_id = "T0"
# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

client = mqtt.Client()


def send_message(message):
    client.publish("message", str(message) + "." + terminal_id, )


def process_message(client, userdata, message):
    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages_log VALUES (?, ?)", (str(message.payload.decode('utf-8')), 1))
    connection.commit()
    connection.close()

    pixels[0] = (0, 255, 0)
    pixels[1] = (0, 255, 0)
    pixels[2] = (0, 255, 0)
    pixels[3] = (0, 255, 0)
    pixels[4] = (0, 255, 0)
    pixels[5] = (0, 255, 0)
    pixels[6] = (0, 255, 0)
    pixels[7] = (0, 255, 0)
    pixels.show()
    GPIO.output(buzzerPin, not True)
    time.sleep(1)
    GPIO.output(buzzerPin, not False)
    pixels[0] = (0, 0, 0)
    pixels[1] = (0, 0, 0)
    pixels[2] = (0, 0, 0)
    pixels[3] = (0, 0, 0)
    pixels[4] = (0, 0, 0)
    pixels[5] = (0, 0, 0)
    pixels[6] = (0, 0, 0)
    pixels[7] = (0, 0, 0)
    pixels.show()

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
    client.connect(broker)
    send_message("Client connected")


def disconnect_from_broker():
    send_message("Client disconnected")
    client.disconnect()


def rfid_read():
    MIFAREReader = MFRC522()
    lastRead = time.time()
    while noEscape:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i * 8)
                    # TODO: num may be nick for sending message
                timestamp = time.time()
                if (timestamp - lastRead) >= 0.5:
                    global text, chatMode
                    print(text)
                    send_message(text)
                    text = ""
                    chatMode = True

                    GPIO.output(buzzerPin, not True)
                    time.sleep(1)
                    GPIO.output(buzzerPin, not False)
                lastRead = time.time()


def load_chat():
    pass
    # TODO: load chat from DB i print it on the screen


def show_chat():
    global chatMode
    chatMode = True
    pass
    # TODO: chat view, scrolling enabled


def show_message():
    global chatMode, text
    chatMode = False

    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

    # print("- draw rectangle")
    draw.rectangle([(5, 5), (90, 30)], fill="BLUE")
    # print("- draw morse")
    draw.text((8, 0), text, font=fontSmall, fill="BLACK")
    # print("- draw symbol")
    if morseCode.get(text) is None:
        draw.text((12, 40), 'ERR', font=fontSmall, fill="BLACK")
    else:
        draw.text((12, 40), morseCode[text], font=fontSmall, fill="BLACK")

    # # image1 = image1.rotate(45)
    # disp.ShowImage(image1, 0, 0)
    # time.sleep(2)

    # disp.clear()
    # disp.reset()


def scroll_up(channel):
    if chatMode:
        pass
        # TODO: scroll up


def scroll_down(channel):
    if chatMode:
        pass
        # TODO: scroll down


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

    rfid_read()

    disconnect_from_broker()


if __name__ == "__main__":
    init()
