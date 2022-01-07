from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorboard
import datetime
import time
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, LSTM, Embedding, GRU, SimpleRNN
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard
import os

WINDOW_SIZE = 4
SLIDING_WINDOW = 1
NO_OF_CLASSES = 2
ARRAY_SIZE = 6

PATIENCE = 10
# NAMES = ["JOVI","LEON","DIX","ZX"]

NAMES = ["data"]
def sliding_window_func(X,y,sliding_window,window_size):
    output_x = []
    output_y = []
    local_window = 0
    iter = int((len(X)/window_size)*(window_size/sliding_window)-(window_size/sliding_window)+1)
    for i in range(iter):
        data_point_x = X[0+local_window:window_size+local_window]
        data_point_y = y[0+local_window]
        output_x.append(np.array(data_point_x))
        output_y.append(np.array(data_point_y))
        local_window += sliding_window

    return np.array(output_x), np.array(output_y)

def read_data():
    headings = {'AX':[],'AY':[],'AZ':[],'GX':[],'GY':[],'GZ':[],'Result':[]}
    x_data = {'AX':[],'AY':[],'AZ':[],'GX':[],'GY':[],'GZ':[]}
    labels = {'Result':[]}
    combined_x = []
    combined_labels = []
    combined_output_x = []
    combined_output_labels = []
    for name in NAMES:
        PATH = str(name)+"/"

        for i in range(0,NO_OF_CLASSES):
            # if(i==3):
            #     continue
            # else:
            print(PATH+str(i+1)+".csv")
            df_local= pd.DataFrame(headings)
            df_local = pd.read_csv(PATH+str(i+1)+".csv")
            if(i==3): print(df_local)
            to_remove = df_local.shape[0]%WINDOW_SIZE
            df_local = df_local.iloc[:-to_remove]
            # df_local = df_local.drop('Time',1)
            no_rows = df_local.shape[0]
            df_local['Result'] = np.full(no_rows,i)
            no_elements = int(df_local.shape[0]/WINDOW_SIZE)
            x_data = df_local.drop('Result', axis=1)
            labels = df_local['Result']
            combined_x.append(x_data.to_numpy())
            combined_labels.append(labels.to_numpy())


        for dataset in combined_x:
            for data in dataset:
                combined_output_x.append(data)
        for dataset in combined_labels:
            for data in dataset:
                combined_output_labels.append(data)

    combined_output_x, combined_output_labels = sliding_window_func(combined_output_x, combined_output_labels, SLIDING_WINDOW, WINDOW_SIZE)

    return combined_output_x, combined_output_labels

X, y = read_data()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)


def CNN(x_train,y_cat_train,X_test,y_cat_test, save=False):
    model = Sequential()

    # CONVOLUTIONAL LAYER
    model.add(Conv1D(filters=16, kernel_size=2, activation='relu',input_shape=(WINDOW_SIZE, ARRAY_SIZE)))
    # POOLING LAYER
    model.add(MaxPooling1D(pool_size=2))
    # FLATTEN IMAGES FROM ARRAY_SIZE by WINDOW_SIZE to 1D BEFORE FINAL LAYER
    model.add(Flatten())
    # 128 NEURONS IN DENSE HIDDEN LAYER (YOU CAN CHANGE THIS NUMBER OF NEURONS)
    model.add(Dense(48, activation='relu'))
    # LAST LAYER IS THE CLASSIFIERS
    model.add(Dense(NO_OF_CLASSES, activation='softmax'))
    opt = tf.keras.optimizers.Nadam(learning_rate=0.001)
    # https://keras.io/metrics/
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer=opt,
                  metrics=['sparse_categorical_accuracy'])

    model.summary()

    early_stop = EarlyStopping(monitor='val_loss',patience=PATIENCE)
    PATH = os.path.join('fall_ml\logs_CNN',datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    tensorboard_callback = keras.callbacks.TensorBoard(log_dir=PATH,profile_batch=0)
    model.fit(x_train,y_cat_train,epochs=50,validation_data=(X_test,y_cat_test), callbacks=[early_stop,tensorboard_callback])

    if save: model.save("FALL_DETECT")

CNN(X_train,y_train,X_test,y_test, True)
