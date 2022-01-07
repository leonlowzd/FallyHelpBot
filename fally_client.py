import serial
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import time

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
    count +=1
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
    # end = time.time()
    # if(count==5):
    #     print(data)
    #     count = 0
    # print(str(end - start)+"s : "+str(move_mapping(output)))
