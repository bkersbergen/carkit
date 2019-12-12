import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow import keras
import tensorflow as tf
from src.server.utils import INPUT_SHAPE, batch_generator
import argparse
import os

np.random.seed(0)

def load_data(args):
    data_df = pd.read_csv(os.path.join(os.getcwd(), args.data_dir, 'driving_log.csv'), names=['center', 'left', 'right', 'steering', 'throttle', 'reverse', 'speed'])

    X = data_df[['center', 'left', 'right']].values
    y = data_df['steering'].values

    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=args.test_size, random_state=42)
    return X_train, X_valid, y_train, y_valid

def s2b(s):
    s = s.lower()
    return s == 'true' or s == 'yes' or s == 'y' or s == '1'

def create_model_functional(args):
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    tf.compat.v1.Session(config=config)
    i = keras.layers.Input(shape=INPUT_SHAPE)
    x = keras.layers.Lambda(lambda x: x / 127.5 - 1.0)(i)
    x = keras.layers.Conv2D(24, kernel_size=5, activation='elu', strides=(2, 2))(x)
    x = keras.layers.Conv2D(36, kernel_size=5, activation='elu', strides=(2, 2))(x)
    x = keras.layers.Conv2D(48, kernel_size=5, activation='elu', strides=(2, 2))(x)
    x = keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = keras.layers.Dropout(args.keep_prob)(x)
    x = keras.layers.Conv2D(64, kernel_size=3, activation='elu')(x)
    x = keras.layers.Conv2D(64, kernel_size=3, activation='elu')(x)
    x = keras.layers.Dropout(args.keep_prob)(x)
    x = keras.layers.Flatten()(x)
    x = keras.layers.Dense(100, activation='elu')(x)
    x = keras.layers.Dropout(args.keep_prob)(x)
    x = keras.layers.Dense(50, activation='elu')(x)
    x = keras.layers.Dropout(args.keep_prob)(x)
    x = keras.layers.Dense(10, activation='elu')(x)
    x = keras.layers.Dense(1)(x)
    model = keras.Model(i, x)
    model.summary()
    return model


def create_model(args):
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    tf.compat.v1.Session(config=config)
    model = keras.Sequential()
    model.add(keras.layers.Lambda(lambda x: x / 127.5 - 1.0, input_shape=INPUT_SHAPE))
    model.add(keras.layers.Conv2D(24, kernel_size=5, activation='elu', strides=(2, 2)))
    model.add(keras.layers.Conv2D(36, kernel_size=5, activation='elu', strides=(2, 2)))
    model.add(keras.layers.Conv2D(48, kernel_size=5, activation='elu', strides=(2, 2)))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    model.add(keras.layers.Dropout(args.keep_prob))
    model.add(keras.layers.Conv2D(64, kernel_size=3, activation='elu'))
    model.add(keras.layers.Conv2D(64, kernel_size=3, activation='elu'))
    model.add(keras.layers.Dropout(args.keep_prob))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(100, activation='elu'))
    model.add(keras.layers.Dropout(args.keep_prob))
    model.add(keras.layers.Dense(50, activation='elu'))
    model.add(keras.layers.Dropout(args.keep_prob))
    model.add(keras.layers.Dense(10, activation='elu'))
    model.add(keras.layers.Dense(1))
    model.summary()

    return model


def train_model(model, args, X_train, X_valid, y_train, y_valid):
    checkpoint = keras.callbacks.ModelCheckpoint('model-{epoch:03d}.h5',
                                 monitor='val_loss',
                                 verbose=0,
                                 save_best_only=args.save_best_only,
                                 mode='auto')
    early_stopping_callback = keras.callbacks.EarlyStopping(monitor='val_loss')
    tensorboard_callback = keras.callbacks.TensorBoard(log_dir='logdir')

    model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(lr=args.learning_rate), metrics=['mse'])

    model.fit_generator(batch_generator(args.data_dir, X_train, y_train, args.batch_size, True),
                        steps_per_epoch=args.steps_per_epoch,
                        epochs=args.nb_epoch,
                        max_queue_size=10,
                        validation_data=batch_generator(args.data_dir, X_valid, y_valid, args.batch_size, False),
                        validation_steps=400,
                        callbacks=[tensorboard_callback],
                        verbose=1)
    model.save('final_model', save_format='tf')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Behavioral Cloning Training Program')
    parser.add_argument('-d', help='data directory', dest='data_dir', type=str, default='E:\\self-driving-car\\IMG')
    parser.add_argument('-t', help='test size fraction', dest='test_size', type=float, default=0.2)
    parser.add_argument('-k', help='drop out probability', dest='keep_prob', type=float, default=0.25)
    parser.add_argument('-n', help='number of epochs', dest='nb_epoch', type=int, default=10)
    parser.add_argument('-s', help='steps per epoch', dest='steps_per_epoch', type=int, default=5500)
    parser.add_argument('-b', help='batch size', dest='batch_size', type=int, default=64)
    parser.add_argument('-o', help='save best models only', dest='save_best_only', type=s2b, default='false')
    parser.add_argument('-l', help='learning rate', dest='learning_rate', type=float, default=1.0e-4)
    args = parser.parse_args()

    # print parameters
    print('-' * 30)
    print('Parameters')
    print('-' * 30)
    for key, value in vars(args).items():
        print('{:<20} := {}'.format(key, value))
    print('-' * 30)

    data = load_data(args)
    model = create_model_functional(args)
    train_model(model, args, *data)