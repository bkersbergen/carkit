# set async_mode to 'threading' (2000ms), 'eventlet' (13ms), 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's installed
async_mode = None

# roundtrip with 640x480px image takes 40ms.

import time
from flask import Flask
import socketio
import json
import os
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO
import numpy as np

from src.server.io import KeyboardIO

sio = socketio.Server(logger=True, async_mode=async_mode, binary=True)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = '7jijasdof!9nasd!f!'
thread = None
store_captured_images = True

my_keyboard_io = KeyboardIO()

@sio.on('telemetry')
def handle_telemetry(sid, data):
    global my_keyboard_io
    car_steering_angle = float(data["_steering_angle"])
    car_throttle = float(data["_throttle"])
    car_speed = float(data["speed"])
    pil_image = Image.open(BytesIO(base64.b64decode(data["image"])))
    if store_captured_images:
        image_location = 'imgs'
        if not os.path.exists(image_location):
            os.makedirs(image_location)
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
        pil_image.save('{}.jpg'.format(os.path.join(image_location, timestamp)))
    kb_throttle, kb_steering = my_keyboard_io.get_throttle_and_steering()
    sio.emit('steer', data={'_steering_angle': kb_steering, '_throttle': kb_throttle, })


if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi

        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi

        try:
            from geventwebsocket.handler import WebSocketHandler

            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file server_app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)
