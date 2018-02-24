from flask import Flask, request
import requests

from threading import Thread

import RPi.GPIO as GPIO
import paho.mqtt.publish as publish
from time import sleep     # this lets us have a time delay (see line 15)
from datetime import datetime
GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering
GPIO.setup(24, GPIO.IN)    # set GPIO25 as input (button)


app = Flask(__name__)

runit=True

ACCESS_TOKEN = "EAADYAWErpa8BAHQxbuH5ZAkfZAZCZCZBumocPs3c8zWTuk3p9fiE5GMSWsJFZBDk9ZCwOPjeLxGGlrVMMwzDVgNEMUD83LNWNaxl8NbXLoIUrXf8k6sh8ZAEpr0aRXhCZBLMyWP7VfTowqEBNC2tMCptzTcE9qj4kxv76LvttG4Y9IrBGjHRj3p9Q"


def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)

def detectsound(sender):
    global runit
    print("listening")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.IN)
    m=0
    soundheard=0
    try:
        while runit:
            m=m+1
            if not GPIO.input(24):
                soundheard=soundheard+1
                sleep(0.05)
            if soundheard >= 5:
                reply(sender,"A sound was detected")
                soundheard=0
                m=0
            if m%1000000==0:
                m=0
                soundheard=0
                print("here"+str(datetime.now())
)
    finally:
        GPIO.cleanup()

@app.route('/', methods=['POST'])
def handle_incoming_messages():
    global runit
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    if message=="start" or message=="Start":
        reply(sender, "Bark-O-Matic is now monitoring for sound")
        runit=True
        t1 = Thread(target = detectsound, args=(sender,))
        t1.daemon = True
        t1.start()

    elif message=="stop" or message=="Stop":
        reply(sender, "Bark-O-Matic has stopped monitoring for sound")
        runit=False

    else:
        reply(sender, "Please enter the command start or stop")

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)
