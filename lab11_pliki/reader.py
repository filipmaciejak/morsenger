#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import sqlite3

broker = 'localhost'
client = mqtt.Client()

def process_message(client, userdata, message):
    connention = sqlite3.connect("messages.db")
    cursor = connention.cursor()
    cursor.execute("INSERT INTO messages_log VALUES (?, ?)",
    (str(message.payload.decode('utf-8')), 1))
    connention.commit()
    connention.close()

    print('RFID scan: ' + str(message.payload.decode('utf-8')))

client.connect(broker)
client.on_message = process_message
client.loop_start()
client.subscribe('rfid/records')
while True:
    pass
