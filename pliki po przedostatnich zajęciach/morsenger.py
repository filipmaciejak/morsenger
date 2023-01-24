#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import board
import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
import neopixel
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import sqlite3


text = ""
chatMode = True
noEscape = True
morseCode = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
             '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
             '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
             '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5',
             '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0', '--..--': ', ', '.-.-.-': '.',
             '..--..--': '?', '-..-.': '/', '-....-': '-', '-.--.': '(', '-.--.-': ')', '.-.-': 'Ą', '-.-..': 'Ć',
             "..--..": 'Ę', '.-..-': 'Ł', '--.--': 'Ń', '---.': 'Ó', '...--...': 'Ś', '--..-.': 'Ż', '--.-': 'Ź'}
pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)

# The broker name or IP address.
broker = "10.108.33.123"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

client = mqtt.Client()


def send_message(nick, message):
    client.publish("message", str(nick) + ': ' + str(message), )
    GPIO.output(buzzerPin, not True)
    time.sleep(1)
    GPIO.output(buzzerPin, not False)


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
    time.sleep(0.1)
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

    print(str(message.payload.decode('utf-8')))


def connect_to_broker():
    client.connect(broker)
    send_message(':::', "Client connected ::::")


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

                    if morseCode.get(text) is None:
                        print('Nierospoznany znak')
                    else:
                        print(morseCode[text])
                        send_message(num, morseCode[text])

                    text = ""
                    chatMode = True
                    show_chat()
                lastRead = time.time()


def load_chat():
    pass
    # TODO: load chat from DB i print it on the screen


def show_chat():
    global chatMode
    chatMode = True
    
    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

# TODO: wyswietl chat
    #draw.text((8, 0), 'chat', font=fontSmall, fill="BLACK")
    #disp.ShowImage(image1, 0, 0)
    row = 0
    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages_log")
    log_entries = cursor.fetchall()
    for a in log_entries:
        draw.text((8, row), a[0], font=fontSmall, fill="BLACK")
        row += 15
        print(a[0])
    print(row)
    disp.ShowImage(image1, 0, row-30)
    connection.commit()
    connection.close()


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

    disp.ShowImage(image1, 0, 0)


def scroll_up(channel):
    if chatMode:
        pass
        # TODO: scroll up


def scroll_down(channel):
    if chatMode:
        pass
        # TODO: scroll down


greenTime = time.time()
def green_start(channel):
    global text, greenTime

    timestamp = time.time()
    if (timestamp - greenTime) >= 0.05:
        text = text + "."
        show_message()
    greenTime = time.time()


redTime = time.time()
def red_start(channel):
    global text, redTime
    
    timestamp = time.time()
    if (timestamp - redTime) >= 0.05:
        text = text + "-"
        show_message()
    redTime = time.time()


def init():
    # save time of pressing the button
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=green_start, bouncetime=50)
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=red_start, bouncetime=50)

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

    show_chat()

    rfid_read()

    disconnect_from_broker()


if __name__ == "__main__":
    init()
