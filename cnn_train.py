import os, glob, numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

import tensorflow as tf

def cnn():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)

    X_train, X_test, Y_train, Y_test = np.load('model/increase_image_data.npy', allow_pickle=True)
    print(X_train.shape)
    print(X_train.shape[0])

    caltech_dir = "./Train"
    categories = os.listdir(caltech_dir)
    nb_classes = len(categories)

    # 일반화
    X_train = X_train.astype(float) / 255
    X_test = X_test.astype(float) / 255

    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding="same", input_shape=X_train.shape[1:], activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))

    model.add(Conv2D(64, (3, 3), padding="same", activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))

    model.add(Conv2D(128, (3, 3), padding="same", activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))


    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model_dir = './model'

    if not os.path.exists(model_dir):
        os.mkdir(model_dir)

    model_path = model_dir + '/CNN.h5'
    checkpoint = ModelCheckpoint(filepath=model_path, monitor='val_loss', verbose=1, save_best_only=True)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5)

    model.summary()

    history = model.fit(X_train, Y_train, batch_size=32, epochs=20, validation_data=(X_test, Y_test),
                        callbacks=[checkpoint, early_stopping])

    print("정확도 : %.4f" % (model.evaluate(X_test, Y_test)[1]))

    y_vacc = history.history['val_accuracy']
    y_vloss = history.history['val_loss']

    x_len = np.arange(len(y_vloss))

    plt.plot(x_len, y_vacc, marker='.', c='red', label='val_accuracy')
    plt.plot(x_len, y_vloss, marker='.', c='blue', label='val_loss')
    plt.legend()
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.grid()
    plt.show()