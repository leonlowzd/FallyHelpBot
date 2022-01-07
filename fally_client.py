import serial
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import time
#import schedule
import requests


def telegram_bot_sendtext(bot_message):

    bot_token = '5011504726:AAEx98q7iS00QsglPhk-vSPIHni11CAhfao'
    bot_chatID = '689229292'
    sender_ID = '43690748'

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def report():
    #my_balance = 10   ## Replace this number with an API call to fetch your account balance
    my_message = "Fall has been detected"   ## Customize your message
    telegram_bot_sendtext(my_message)


#schedule.every().day.at("12:00").do(report)


WINDOW_SIZE = 4
SLIDING_WINDOW = 1
ARRAY_SIZE = 6
PATH = 'FALL_DETECT'
def move_mapping(result):
    move = ""
    if result == [0]:
        move = 'Fall'
    else:
        move = 'No Fall'

def read_set(arduino):
    output_x = []
    for i in range(WINDOW_SIZE):
        msg = arduino.readline().decode()
        msg = str(msg).strip('\r\n').split(',')
        output_x.append(msg)
    return np.array(output_x)


arduino = serial.Serial(port='COM3', baudrate=115200, timeout=100)
loaded_model = tf.keras.models.load_model((PATH))
loaded_model.summary()
time.sleep(10)
arduino.reset_input_buffer()
arduino.reset_output_buffer()
arduino.flush()
count = 0
while(1):
    output_x = []
    start = time.time()
    for i in range(WINDOW_SIZE):
        dataset = []
        msg = arduino.read_until().decode()
        msg = str(msg).strip('\r\n').split(',')
        for data in msg:
            dataset.append(float(data))
        output_x.append(dataset)
    data = np.array([output_x])
    output = np.argmax(loaded_model.predict(data), axis=-1)
    print(output)
    if (output == 0) :
        report()
        time.sleep(20)
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        arduino.flush()
    else:
        count = 0
