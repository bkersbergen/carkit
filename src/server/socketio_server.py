import argparse
import base64
from datetime import datetime
import os
import shutil
import numpy as np
import socketio
import eventlet
import eventlet.wsgi
from PIL import Image
from flask import Flask
from io import BytesIO

from src.server.io import KeyboardIO
from tensorflow import keras

from src.server import utils

sio = socketio.Server()
app = Flask(__name__)
model = None
prev_image_array = None

# set min/max speed for our autonomous car
MAX_SPEED = 25
MIN_SPEED = 10

# and a speed limit
speed_limit = MAX_SPEED


# registering event handler for the server
@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        # The current steering angle of the car
        steering_angle = float(data["_steering_angle"])
        # The current _throttle of the car, how hard to push peddle
        throttle = float(data["_throttle"])
        # The current speed of the car
        speed = float(data["speed"])
        # The current image from the center camera of the car
        pil_image = Image.open(BytesIO(base64.b64decode(data["image"])))
        try:
            image = np.asarray(pil_image)  # from PIL image to numpy array
            image = utils.preprocess(image)  # apply the preprocessing
            image = np.array([image],  dtype=np.float32)  # the model expects 4D array

            # predict the steering angle for the image
            steering_angle = float(model.predict(image, batch_size=1))
            # lower the _throttle as the speed increases
            # if the speed is above the current speed limit, we are on a downhill.
            # make sure we slow down first and then go back to the original max speed.
            global speed_limit
            if speed > speed_limit:
                speed_limit = MIN_SPEED  # slow down
            else:
                speed_limit = MAX_SPEED
            throttle = 1.0 - steering_angle ** 2 - (speed / speed_limit) ** 2

            print('adjustments steering:{:g} _throttle:{:g} speed:{:g}'.format(steering_angle, throttle, speed))
            send_control(steering_angle, throttle)
        except Exception as e:
            print(e)

        # save frame
        if args.image_folder != '':
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename = os.path.join(args.image_folder, timestamp)
            pil_image.save('{}.jpg'.format(image_filename))
    else:
        sio.emit('manual', data={}, skip_sid=True)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid, environ)
    send_control(0, 0)


def send_control(steering_angle, throttle):
    sio.emit(
        "steer",
        data={
            '_steering_angle': steering_angle.__str__(),
            '_throttle': throttle.__str__()
        },
        skip_sid=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument(
        'model',
        type=str,
        help='Path to model h5 file. Model should be on the same path.',
    )
    parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        help='Path to image folder. This is where the images from the run will be saved.'
    )
    args = parser.parse_args()

    # load model
    import tensorflow as tf
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    sess = tf.compat.v1.Session(config=config)
    model = keras.models.load_model('final_model')

    if args.image_folder != '':
        print("Creating image folder at {}".format(args.image_folder))
        if not os.path.exists(args.image_folder):
            os.makedirs(args.image_folder)
        else:
            shutil.rmtree(args.image_folder)
            os.makedirs(args.image_folder)
        print("RECORDING THIS RUN ...")
    else:
        print("NOT RECORDING THIS RUN ...")

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
